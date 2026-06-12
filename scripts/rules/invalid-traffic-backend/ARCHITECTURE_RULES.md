# Invalid Traffic Backend — Architecture Diagram

Tài liệu này mô tả cấu trúc và quy tắc của dự án `invalid-traffic-backend-go` (Go).
Mục đích: Hỗ trợ AI và Developer hiểu rõ vị trí và trách nhiệm từng thành phần để review, maintain và refactor an toàn.

## Cấu trúc tổng quan

Nhận signals từ JS SDK, chạy qua các bộ lọc GIVT rồi tính điểm SIVT để phân loại traffic là human hay bot/invalid. Trả về `sivt_risk_score`.

### 1. Entry point & DI
* `cmd/api/`: Khởi động server, load env. Wire DI assembles `Config → Redis → SnapshotService → TrafficPipelineService → HTTP handlers`. Sau mỗi lần đổi provider, chạy `wire ./cmd/api/`.
* `cmd/tools/`: CLI tools một lần — convert blacklist/whitelist/UA data sang Redis snapshot.

### 2. HTTP Layer (`internal/app/api/`)
* `router/`: Đăng ký routes, mount middleware.
* `controller/traffic.go`: Parse body → build `TrafficPipelineContext` → gọi pipeline → map output sang response.
* `middleware/`: CORS, logging, panic recovery, ETag.
* `binding/dce.go`: `NormalizedPayload` — canonical struct cho toàn bộ JS SDK payload.

### 3. Pipeline (`internal/service/`)
* `traffic_pipeline.go`: `TrafficPipelineService` — orchestrate toàn bộ GIVT + SIVT theo thứ tự cố định. Matchers GIVT-01/02 lưu trong `atomic.Pointer` để hot-swap không lock.
* `snapshot.go`: Load/reload GIVT-01 và GIVT-02 data từ Redis snapshot; pub/sub subscriber trigger hot-reload khi có thay đổi.
* `givt01/` → `givt05/`: Mỗi bộ lọc GIVT là package riêng biệt.
* `sivtl0/`, `sivtl1m1/` → `sivtl1m3/`, `sivtl2bcs/`, `sivtl2clis/`, `sivtl2nas/`, `sivtl2sas/`, `sivtl2/`: Các module SIVT.
* `sivt/config.go`: Toàn bộ weights, thresholds, hard floors — nguồn sự thật duy nhất cho scoring config.

### 4. Infrastructure & Config
* `internal/db/`: Tạo `pgxpool.Pool` và `redis.Client`.
* `internal/config/config.go`: Đọc toàn bộ biến môi trường qua `caarlos0/env`.
* `internal/common/`: `APIError`, `APIResponse`, enums dùng chung.


# Invalid Traffic Backend — Architectural Guidelines & Context cho AI

## 1. Tổng quan dự án

**JS SDK** (`IvtSendUserSummary`) → **`POST /v1/check-traffic`** → parse `NormalizedPayload` → pipeline GIVT → SIVT scoring → trả về `{ action, sivt_risk_score, trace[] }`.

- `action = "NO_BID"`: traffic invalid, bị block tại một GIVT stage hoặc SIVT score cao.
- `action = "PASS"`: vượt qua tất cả filters, được coi là human traffic.

Stack: **Gin · Redis · Google Wire · zerolog**.

## 2. Pipeline chi tiết

### GIVT — Bộ lọc cơ bản (sequential, short-circuit)

Mỗi bước fail → trả `NO_BID` ngay, không chạy tiếp:

| Stage | Package | Cơ chế |
|-------|---------|---------|
| GIVT-03 Malformed | `givt03/` | Validate IP (missing/bogon/malformed/WebRTC mismatch), schema payload |
| GIVT-04 Prefetch | `givt04/` | Detect browser prefetch/prerender qua request headers |
| GIVT-01 Datacenter/Proxy | `givt01/` | Match IP/CIDR/ASN vs blacklist trong RAM (`atomic.Pointer`) |
| GIVT-02 Non-Human Bot | `givt02/` | Match UA vs bot signatures trong RAM, FCrDNS verification |
| GIVT-05 Velocity | `givt05/` | Rate limit per IP qua Redis sliding window |

GIVT-01 và GIVT-02 matchers load từ Redis snapshot lúc startup, hot-reload qua Redis Pub/Sub — không cần restart server.

### SIVT — Tính điểm (nếu qua hết GIVT)

**L0 — Hard Block** (`sivtl0/`): Check một số signal cứng. Nếu triggered → `sivt_risk_score = 1.0`, bỏ qua L1/L2.

**L1 — Risk Score** (weighted average, 3 module đang active):

| Module | Package | Mô tả | Weight |
|--------|---------|-------|--------|
| M1 | `sivtl1m1/` | Headless / Automation detection | 0.30 |
| M2 | `sivtl1m2/` | Device Fingerprint anomalies (GPU, audio, screen) | 0.15 |
| M3 | `sivtl1m3/` | Network Anomaly (IP type, geo, WebRTC) | 0.25 |

Nếu L1 score ≥ 0.60 → dùng L1 score làm final, bỏ qua L2.

**L2 — Coherence-Weighted Aggregation** (`sivtl2/`):

| Sub-score | Package | Mô tả | Weight |
|-----------|---------|-------|--------|
| BCS | `sivtl2bcs/` | Behavioral Coherence (scroll/click/audio incoherence) | 0.40 |
| CLIS | `sivtl2clis/` | Cross-Layer Inconsistency (UA vs TLS/JA4/HTTP) | 0.20 |
| NAS | `sivtl2nas/` | Network Anomaly (JA4 bot, fraud proxy, geo-TZ) | 0.25 |
| SAS | `sivtl2sas/` | Server Anomaly (bid request inconsistency) | 0.15 |

L2 có Coherence Amplification: nếu K ≥ 3 independent signals triggered → score được khuếch đại. Hard floors của individual signals ghi đè base score nếu cao hơn.

**Final score**: `max(L1, L2 coherence_score)`.

## 3. Quy tắc làm việc & dependency

1. **Giữ đúng tầng:** `cmd/ → app/api/ → service/ → db/`. Controller không gọi Redis/DB trực tiếp. Pipeline service không import `gin`.
2. **`TrafficPipelineContext` là shared state:** Mọi output của mỗi stage phải ghi vào đúng field trong `TrafficPipelineContext`. Không truyền output riêng lẻ giữa các stage.
3. **Thứ tự pipeline cố định:** GIVT-03 → GIVT-04 → GIVT-01 → GIVT-02 → GIVT-05 → SIVT. Không thay đổi thứ tự này.
4. **GIVT short-circuit:** Stage nào fail phải return sớm, không chạy tiếp. Mỗi stage append một `FilterTrace` vào `ctx.Trace` để observability.
5. **Matchers trong RAM:** GIVT-01 và GIVT-02 dùng `atomic.Pointer` — không lock hot path. Reload qua `ReloadGIVT01()` / `ReloadGIVT02()`, không khởi tạo lại service.
6. **Scoring config tập trung tại `sivt/config.go`:** Mọi weight, threshold, hard floor phải định nghĩa ở đây. Không hardcode số trong các module scoring.
7. **Signal mới cho SIVT — 2 chỗ:** `Extract*Signals()` (đọc từ `NormalizedPayload`) và `CheckSignals()` (đánh giá từng signal). Không thêm logic scoring vào Extract.
8. **`NormalizedPayload` là read-only trong pipeline:** Không modify payload sau khi parse. Mọi enrichment (server IP, network data) phải được binding layer inject trước khi vào pipeline.
9. **Config từ env:** Không hardcode URL, Redis addr, threshold động. Đọc từ `internal/config/config.go`.
10. **Redis optional cho GIVT-01/02:** Nếu snapshot chưa có trong Redis, stage PASS (không block). Log warn, không panic.

## 4. Quy ước đặt tên

- **Package:** lowercase theo chức năng — `givt01`, `sivtl1m1`, `sivtl2bcs`.
- **File:** `snake_case` theo vai trò — `scoring.go`, `device_signals.go`, `matcher.go`.
- **Struct:** PascalCase — `TrafficPipelineService`, `TrafficPipelineContext`, `FilterTrace`.
- **Stage output:** `*givtXX.Output` hoặc `*sivtYY.Score` — pointer, nil khi stage chưa chạy.
- **Rule code:** `UPPER_SNAKE_CASE` với prefix stage — `GIVT_01_CLD_AZURE`, `GIVT_03_IP_BOGON`.
- **Error:** `fmt.Errorf("context: %w", err)`. Không panic trong pipeline.

## 5. Nguyên tắc refactor cho AI

- Bảo toàn response shape `{ action, sivt_risk_score, trace[] }` — contract với JS SDK.
- Không đổi thứ tự GIVT stages hay SIVT L0→L1→L2 — có chủ đích (cheap checks trước, scoring sau).
- Không sửa weights/thresholds/hard floors trong `sivt/config.go` khi chưa được yêu cầu rõ ràng.
- Khi thêm GIVT stage mới: thêm vào `run()` đúng vị trí, định nghĩa stage constant trong `ivt_enums.go`.
- Khi thêm SIVT module mới (M4–M6): thêm weight trong `sivt/config.go`, wire vào L1 weighted average trong `extractSIVTDeviceSignals()`.
- Sau khi đổi Wire provider, chạy `wire ./cmd/api/` và commit `wire_gen.go`.
- Ưu tiên thay đổi nhỏ, đúng tầng, dễ review.
