# Identity Graph Backend (Go) — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của `identity-graph-backend-go`. Căn cứ: 📐 Coding Standards — Backend Go/Gin v1.0 (luật dưới đây thay thế các mục Go chung khi khác nhau, ví dụ DB là PostgreSQL thay vì Mongo).
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.

## 1. Tổng quan
**JS SDK** (`IdtSendUserSummary`) → **Cloudflare Worker** (CORS, forward) → **`POST /v1/user-idt`** → `Collect()` parse signals → pipeline 4 bước → cập nhật DB → trả `{ node_id, action, step }`.
Mục tiêu: cùng một người dùng thực luôn nhận cùng `node_id` dù đổi browser, xoá cookie hay vào từ site khác. Traffic lớn, yêu cầu high availability, low latency.
Stack: **Gin · pgxpool (PostgreSQL, DB `identity_graph`) · Redis · Google Wire · logrus**.

### Pipeline 4 bước (bước nào match thì short-circuit)
| Bước | File | Cơ chế | Kết quả |
|---|---|---|---|
| 1 Same Person | `step_same_person.go` | `hashed_email` → Redis → Postgres | MERGE |
| 2 Same Site | `step_same_site.go` | `publisher_uuid` → `TemporaryID` → Redis → Postgres | MERGE |
| 3 Cross Site | `step_cross_site.go` | Fast scoring → Hard scoring; ≥80/75 merge, ≥40/60 link | MERGE / LINK |
| 4 Cross Device | `step_cross_device.go` | Fallback | CREATE |

`TemporaryID` ưu tiên: `server_cookie_id > third_cookie_id > ppid_cookie > indexed_db_id > local_storage_id`.

## 2. Cấu trúc thư mục & trách nhiệm
- `cmd/api/`: khởi động server, load env, chạy migration; Wire: `Config → pgxpool + Redis → IdentityService → HTTP handlers`.
- `cmd/worker/`: background job kiểu cron; không chạy migration; job guard bằng Postgres advisory lock.
- `internal/app/api/`: `router/`, `controller/` (mỏng), `middleware/` (auth, CORS, logging, recovery), `binding/`.
- `internal/service/`: lớp mỏng nối `identity/` với handler; không query DB, không chứa scoring.
- `internal/identity/`: toàn bộ logic định danh — `collector.go` (body + header → `Signals`), `signal.go` (`SignalValueMap()`, `signalWeightsV2`, `signalTTLDaysV2`, `resolveTemporaryID()`), `resolver.go` (orchestrate pipeline, audit event async), `step_*.go`, `repository.go` (toàn bộ DB access), `cache.go` (key `idt:sig:{type}:{value}`), `scoring_table.go` (`ComputeScore`), `cleanup_job.go`.
- `internal/infrastructure/` (pgxpool, redis, migration), `internal/job/` (`Job`, `Scheduler`, `PgLocker`), `internal/config/config.go` (`caarlos0/env`), `internal/common/` (`APIError`, `APIResponse`).

## 3. Luật review

### 3.1. Ranh giới tầng — `cmd → app/api → service → identity → infrastructure`
- [chặn merge] Controller hoặc `service/` query DB/Redis trực tiếp; SQL nằm ngoài `identity/repository.go` (hoặc file repository tương đương). [📐 Go §4.2]
- [chặn merge] `identity/` import `gin` (ngoại lệ duy nhất: `collector.go`). [📐 Go §2]
- [chặn merge] Tạo kết nối ad-hoc (`pgx.Connect`, `redis.NewClient`) thay vì dùng `pgxpool.Pool`/client từ Wire. [📐 Go §2.1; Go §8]
- [chặn merge] Sửa tay `wire_gen.go`. [📐 Go §2.1]
- [cảnh báo] Scoring/logic định danh đặt ngoài `internal/identity/`. [Dự án]

### 3.2. Hot path `POST /v1/user-idt` (≤ 80ms end-to-end)
- [chặn merge] Query mới trên hot path không dùng index (full scan, `LIKE '%...'`, unbounded fan-out, N+1 trong vòng lặp). [Dự án]
- [chặn merge] Ghi audit event đồng bộ trong transaction hoặc làm fail request khi audit lỗi (phải dispatch qua channel, lỗi chỉ `log.Warn`). [Dự án]
- [cảnh báo] Bỏ bước Redis L1: tra Postgres trước khi check cache `idt:sig:{type}:{value}`; cache miss không warm lại Redis. [Dự án]
- [cảnh báo] Thêm gọi mạng/IO đồng bộ mới trên hot path không có timeout. [📐 Go §7]
- [cảnh báo] Redis lỗi làm panic/fail request thay vì degrade sang Postgres-only. [Dự án]

### 3.3. Pipeline & scoring
- [chặn merge] Đổi thứ tự 4 bước hoặc logic short-circuit (deterministic trước, probabilistic sau) mà PR không ghi rõ lý do. [Dự án]
- [cảnh báo] Đổi ngưỡng scoring (≥80/75 merge, ≥40/60 link), weight hoặc TTL mà PR không ghi rõ yêu cầu. [Dự án]
- [cảnh báo] Signal mới không thêm đủ 3 chỗ trong `signal.go`: `SignalValueMap()`, `signalWeightsV2`, `signalTTLDaysV2`; hardcode weight/TTL ngoài các map này. [Dự án]
- [cảnh báo] Đổi thứ tự ưu tiên `TemporaryID`. [Dự án]

### 3.4. Contract & dữ liệu
- [chặn merge] Đổi shape response `{ node_id, action, step }` (contract với JS SDK). [📐 Core §4.3]
- [chặn merge] Lưu hoặc log raw PII/payload (email, IP thô, cookie id gốc khi chưa hash); chỉ lưu ID đã hash/pseudonymize. [📐 Go §11; Core §7]
- [cảnh báo] Đổi schema bảng (`identity_nodes`, `identity_signals`...) mà không có migration mới. [Dự án]
- [cảnh báo] Job mới trong worker không guard bằng advisory lock (`PgLocker`) khi có thể chạy nhiều instance. [Dự án]

### 3.5. Lỗi, context, cấu hình
- [chặn merge] `panic` trong logic nghiệp vụ/pipeline. [📐 Go §6]
- [cảnh báo] Lỗi không bọc `fmt.Errorf("...: %w", err)`; so sánh lỗi bằng chuỗi. [📐 Go §6]
- [cảnh báo] Hardcode URL, DSN, credential thay vì `internal/config/config.go`. [📐 Go §11]
- [cảnh báo] Hàm I/O mới không nhận `context.Context`; goroutine mới không dừng theo context. [📐 Go §7]

### 3.6. Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.
- [cảnh báo] Sửa một bước pipeline, `ComputeScore`, ngưỡng hoặc map trong `signal.go` mà PR không có test cho bước/ngưỡng đó (match → short-circuit; không match → bước sau) — CHỈ khi thay đổi đổi hành vi (thêm/sửa nhánh, điều kiện, ngưỡng, kết quả) VÀ PR không thêm/sửa case test nào cho phần đó VÀ (nếu đọc được repo) test hiện có chưa kiểm hành vi mới; refactor không đổi hành vi thì KHÔNG báo. [📐 Test Go §7.1]
- [cảnh báo] Test cache không có cả nhánh Redis hit, miss (warm lại) và Redis lỗi (degrade sang Postgres). [📐 Test Go §7.1]
- [cảnh báo] Unit test dùng `pgxpool`/Redis thật thay vì mock repository/cache; integration test thiếu `//go:build integration`. [📐 Test Go §2.5; Test Go §3.2]

## 4. Quy ước đặt tên
- [nit] Package chữ thường; file `snake_case.go`; struct PascalCase; constructor `NewXxx`; bảng/cột DB `snake_case`. [📐 Go §12]

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- `collector.go` import `gin` là có chủ đích.
- (Bổ sung tại đây các mẫu báo sai lặp lại mà dev đã xác nhận.)

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Sau khi đổi Wire provider, chạy `wire ./cmd/api/` và commit `wire_gen.go`.
- Không sửa thresholds/weights/TTL khi chưa được yêu cầu. Ưu tiên thay đổi nhỏ, đúng tầng.
