# Invalid Traffic Backend (Go) — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của `invalid-traffic-backend-go`. Căn cứ: 📐 Coding Standards — Backend Go/Gin v1.0 (luật dưới đây thay thế các mục Go chung khi khác nhau).
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.

## 1. Tổng quan
**JS SDK** (`IvtSendUserSummary`) → **`POST /v1/check-traffic`** → parse `NormalizedPayload` → pipeline GIVT → SIVT scoring → trả `{ action, sivt_risk_score, trace[] }`.
- `action = "NO_BID"`: bị chặn ở một stage GIVT hoặc SIVT score cao. `action = "PASS"`: coi là human traffic.
Stack: **Gin · Redis · Google Wire · zerolog**.

### GIVT (tuần tự, short-circuit; fail → `NO_BID` ngay)
GIVT-03 Malformed (`givt03/`) → GIVT-04 Prefetch (`givt04/`) → GIVT-01 Datacenter/Proxy (`givt01/`, matcher RAM `atomic.Pointer`) → GIVT-02 Non-Human Bot (`givt02/`, UA + FCrDNS) → GIVT-05 Velocity (`givt05/`, Redis sliding window). GIVT-01/02 load từ Redis snapshot lúc startup, hot-reload qua Redis Pub/Sub.

### SIVT (khi qua hết GIVT)
- L0 Hard Block (`sivtl0/`): triggered → score = 1.0, bỏ L1/L2.
- L1 weighted average: M1 Headless/Automation 0.30 · M2 Device Fingerprint 0.15 · M3 Network Anomaly 0.25. L1 ≥ 0.60 → dùng L1, bỏ L2.
- L2 Coherence-Weighted: BCS 0.40 · CLIS 0.20 · NAS 0.25 · SAS 0.15; K ≥ 3 signal độc lập → khuếch đại; hard floor ghi đè nếu cao hơn.
- Final = `max(L1, L2 coherence_score)`. Mọi weight/threshold/hard floor nằm ở `sivt/config.go`.

## 2. Cấu trúc thư mục & trách nhiệm
- `cmd/api/`: Wire `Config → Redis → SnapshotService → TrafficPipelineService → handlers`. `cmd/tools/`: CLI chuyển blacklist/whitelist/UA data sang Redis snapshot.
- `internal/app/api/`: `router/`, `controller/traffic.go` (parse body → build `TrafficPipelineContext` → gọi pipeline → map response), `middleware/` (CORS, logging, recovery, ETag), `binding/dce.go` (`NormalizedPayload`).
- `internal/service/`: `traffic_pipeline.go` (orchestrate GIVT + SIVT theo thứ tự cố định), `snapshot.go` (load/reload GIVT-01/02), `givt01/`…`givt05/`, các package `sivt*`, `sivt/config.go`.
- `internal/db/` (pgxpool, redis), `internal/config/config.go` (`caarlos0/env`), `internal/common/` (`APIError`, `APIResponse`, enum).

## 3. Luật review

### 3.1. Ranh giới tầng — `cmd → app/api → service → db`
- [chặn merge] Controller gọi Redis/DB trực tiếp; package pipeline/stage import `gin`. [📐 Go §2; Go §4.2]
- [chặn merge] Sửa tay `wire_gen.go`. [📐 Go §2.1]
- [cảnh báo] Logic scoring/lọc đặt trong controller hoặc binding. [📐 Go §3.3]

### 3.2. Pipeline
- [chặn merge] Đổi thứ tự GIVT-03 → 04 → 01 → 02 → 05 → SIVT, hoặc thứ tự L0 → L1 → L2, mà PR không ghi rõ lý do. [Dự án]
- [chặn merge] Stage GIVT fail mà không return sớm (vẫn chạy tiếp stage sau). [Dự án]
- [chặn merge] Hot path dùng lock (`Mutex`) cho matcher GIVT-01/02 thay vì `atomic.Pointer`; reload bằng cách khởi tạo lại service thay vì `ReloadGIVT01()`/`ReloadGIVT02()`. [Dự án]
- [chặn merge] Sửa `NormalizedPayload` sau khi parse (payload read-only trong pipeline; enrichment phải inject ở binding trước khi vào pipeline). [Dự án]
- [cảnh báo] Output của stage không ghi vào đúng field của `TrafficPipelineContext`, hoặc truyền output rời giữa các stage. [Dự án]
- [cảnh báo] Stage mới không append `FilterTrace` vào `ctx.Trace`; stage mới không có constant trong `ivt_enums.go`. [Dự án]
- [cảnh báo] Signal SIVT mới không đủ 2 chỗ: `Extract*Signals()` (chỉ đọc payload) và `CheckSignals()` (đánh giá); đưa logic scoring vào Extract. [Dự án]

### 3.3. Scoring config
- [chặn merge] Hardcode weight/threshold/hard floor trong module scoring thay vì `sivt/config.go`. [📐 Go §11]
- [cảnh báo] Đổi giá trị trong `sivt/config.go` mà PR không ghi rõ yêu cầu. [Dự án]
- [cảnh báo] Module SIVT mới không thêm weight vào `sivt/config.go` hoặc không wire vào L1 weighted average. [Dự án]

### 3.4. Contract, lỗi, cấu hình
- [chặn merge] Đổi shape response `{ action, sivt_risk_score, trace[] }` (contract với JS SDK). [📐 Core §4.3]
- [chặn merge] `panic` trong pipeline. [📐 Go §6]
- [cảnh báo] Redis snapshot GIVT-01/02 chưa có làm block hoặc panic thay vì PASS + `log.Warn`. [Dự án]
- [cảnh báo] Hardcode URL, Redis addr, threshold động thay vì `internal/config/config.go`. [📐 Go §11]
- [cảnh báo] Lỗi không bọc `%w`; log raw IP/UA kèm định danh người dùng ở mức info. [📐 Go §6; Go §11]

### 3.5. Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.
- [cảnh báo] Stage GIVT/module SIVT MỚI, hoặc sửa làm đổi kết quả lọc/điểm, mà PR không có test: input hợp lệ → PASS; input vi phạm → `NO_BID` + `FilterTrace` đúng rule code; với SIVT: điểm đúng theo weight trong `sivt/config.go` — CHỈ khi thay đổi đổi hành vi (thêm/sửa nhánh, điều kiện, ngưỡng, kết quả) VÀ PR không thêm/sửa case test nào cho phần đó VÀ (nếu đọc được repo) test hiện có chưa kiểm hành vi mới; refactor không đổi hành vi thì KHÔNG báo. [📐 Test Go §7.1]
- [cảnh báo] Test scoring hardcode weight/threshold thay vì đọc từ `sivt/config.go` (test sẽ không bắt được khi đổi config). [Dự án]
- [nit] Thiếu case snapshot Redis chưa có → stage PASS cho GIVT-01/02. [📐 Test Go §7.1]

## 4. Quy ước đặt tên
- [nit] Package theo chức năng chữ thường (`givt01`, `sivtl1m1`); file `snake_case.go`; struct PascalCase. [📐 Go §12]
- [nit] Stage output là pointer (`*givtXX.Output`, `*sivtYY.Score`), nil khi stage chưa chạy. [Dự án]
- [nit] Rule code `UPPER_SNAKE_CASE` có prefix stage (`GIVT_01_CLD_AZURE`, `GIVT_03_IP_BOGON`). [Dự án]

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- Chỉ 3 module L1 (M1–M3) đang active; M4–M6 chưa có — không báo "thiếu module".
- (Bổ sung tại đây các mẫu báo sai lặp lại mà dev đã xác nhận.)

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Thêm GIVT stage: thêm vào `run()` đúng vị trí, định nghĩa constant trong `ivt_enums.go`.
- Thêm module SIVT: weight trong `sivt/config.go`, wire vào L1 trong `extractSIVTDeviceSignals()`.
- Sau khi đổi Wire provider, chạy `wire ./cmd/api/` và commit `wire_gen.go`. Ưu tiên thay đổi nhỏ, đúng tầng.
