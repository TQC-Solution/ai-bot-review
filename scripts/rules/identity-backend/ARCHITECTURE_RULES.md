# Identity Graph Backend — Architecture Diagram

Tài liệu này mô tả cấu trúc và quy tắc của dự án `identity-graph-backend-go` (Go).
Mục đích: Hỗ trợ AI và Developer hiểu rõ vị trí và trách nhiệm từng thành phần để review, maintain và refactor an toàn.

## Cấu trúc tổng quan

Nhận signals từ JS SDK (qua Cloudflare Worker), chạy pipeline các bước để resolve ra `node_id` ổn định đại diện cho cùng một người dùng/thiết bị. Thiết kế cho traffic lớn, yêu cầu high availability và low latency.

### 1. Entry point & DI
* `cmd/api/`: Khởi động server, load env, chạy migration. Wire DI assembles `Config → pgxpool + Redis → IdentityService → HTTP handlers`. Sau mỗi lần đổi provider, chạy `wire ./cmd/api/`.
* `cmd/worker/`: Process riêng cho background jobs (cron-style). Không chạy migration. Jobs guard bằng Postgres advisory lock để tránh double-run khi scale.

### 2. HTTP Layer (`internal/app/api/`)
* `router/`: Đăng ký routes, mount middleware.
* `controller/`: Parse request → gọi service → trả response. Handler phải mỏng, không có business logic.
* `middleware/`: Auth, CORS, logging, panic recovery.
* `binding/`: Bind và validate request body/header.

### 3. Service Layer (`internal/service/`)
Thin layer nối `internal/identity/` với HTTP handlers. Không query DB trực tiếp, không chứa scoring logic.

### 4. Identity Domain (`internal/identity/`)
Toàn bộ logic định danh tập trung ở đây:
* `collector.go`: Parse JSON body + headers thành `Signals`.
* `signal.go`: `Signals` struct, `SignalValueMap()`, signal weights + TTLs, `resolveTemporaryID()`.
* `resolver.go`: Orchestrate pipeline 4 bước, dispatch audit event bất đồng bộ.
* `step_same_person.go` → `step_cross_device.go`: 4 bước pipeline.
* `repository.go`: Toàn bộ DB access.
* `cache.go`: Redis helpers — key pattern `idt:sig:{type}:{value}`.
* `scoring_table.go`: `ComputeScore(matched, fastOnly)` → (score, conf).
* `cleanup_job.go`: Xoá signals hết hạn theo batch.

### 5. Infrastructure & Config
* `internal/infrastructure/`: Tạo `pgxpool.Pool`, `redis.Client`. Migration tự chạy lúc startup.
* `internal/job/`: `Job` interface, `Scheduler`, `PgLocker` — framework cho background jobs.
* `internal/config/config.go`: Đọc toàn bộ biến môi trường qua `caarlos0/env`.
* `internal/common/`: `APIError`, `APIResponse` dùng chung.


# Identity Graph Backend — Architectural Guidelines & Context cho AI

## 1. Tổng quan dự án

**JS SDK** (`IdtSendUserSummary`) → **Cloudflare Worker** (CORS, forward request) → **`POST /v1/user-idt`** → `Collect()` parse signals → pipeline 4 bước → update DB → trả về `{ node_id, action, step }`.

Mục tiêu: cùng một người dùng thực luôn nhận về cùng `node_id` dù đổi browser, xóa cookie, hay vào từ site khác.

Stack: **Gin · pgxpool (PostgreSQL) · Redis · Google Wire · logrus**.

## 2. Pipeline 4 bước

Bước nào match trước thì short-circuit, không chạy tiếp:

| Bước | File | Cơ chế | Kết quả |
|------|------|---------|---------|
| 1 — Same Person | `step_same_person.go` | `hashed_email` → Redis → Postgres | MERGE |
| 2 — Same Site | `step_same_site.go` | `publisher_uuid` → `TemporaryID` → Redis → Postgres | MERGE |
| 3 — Cross Site | `step_cross_site.go` | Fast scoring → Hard scoring; ≥80/75 merge, ≥40/60 link | MERGE / LINK |
| 4 — Cross Device | `step_cross_device.go` | Fallback | CREATE |

**TemporaryID** priority: `server_cookie_id > third_cookie_id > ppid_cookie > indexed_db_id > local_storage_id`

## 3. Quy tắc làm việc & dependency

1. **Giữ đúng tầng:** `cmd/ → app/api/ → service/ → identity/ → infrastructure/`. Controller không query DB trực tiếp. `identity/` không import `gin` (ngoại trừ `collector.go`).
2. **Hot path ≤ 80ms:** Mọi thay đổi trên `POST /v1/user-idt` phải giữ end-to-end ≤ 80ms.
3. **Redis L1 trước:** Check cache `idt:sig:{type}:{value}` trước khi hit Postgres. Cache miss → Postgres → warm Redis.
4. **Không full-table scan:** Query hot path phải dùng index — O(1) hoặc O(log N), không unbounded fan-out.
5. **Audit event ngoài transaction:** Dispatch qua channel, flush async. Lỗi chỉ `log.Warn`, không fail request.
6. **Signal mới — 3 chỗ trong `signal.go`:** `SignalValueMap()`, `signalWeightsV2`, `signalTTLDaysV2`. Không hardcode weight/TTL ngoài maps này.
7. **Connection pooling:** Luôn dùng `pgxpool.Pool` từ Wire. Không `pgx.Connect()` ad-hoc.
8. **Config:** Không hardcode URL, DSN, credential. Đọc từ `internal/config/config.go`. DB là `identity_graph`.
9. **Privacy:** Chỉ lưu hashed/pseudonymized ID. Không log raw payload có PII.
10. **Redis optional:** Degrade gracefully sang Postgres-only khi Redis unreachable — không panic.

## 4. Quy ước đặt tên

- **Package:** lowercase — `identity`, `service`, `config`, `infrastructure`.
- **File:** `snake_case` — `step_same_person.go`, `scoring_table.go`.
- **Struct:** PascalCase — `IdentityService`, `Resolver`, `Signals`, `ResolveResult`.
- **Constructor:** prefix `New` — `NewResolver(repo)`, `NewIdentityService(pool, rdb)`.
- **Error:** `fmt.Errorf("context: %w", err)`. Không panic trong business logic.
- **DB:** `snake_case` — `identity_nodes`, `identity_signals`. Không đổi schema khi chưa có migration mới.

## 5. Nguyên tắc refactor cho AI

- Bảo toàn response shape `{ node_id, action, step }` — contract với JS SDK.
- Không đổi thứ tự pipeline hay logic short-circuit — deterministic trước, probabilistic sau.
- Không sửa scoring thresholds (≥80/75 merge, ≥40/60 link) hay weights/TTLs khi chưa được yêu cầu.
- Không thêm query không có index vào hot path.
- Sau khi đổi Wire provider, chạy `wire ./cmd/api/` và commit `wire_gen.go`.
- Ưu tiên thay đổi nhỏ, đúng tầng, dễ review.
