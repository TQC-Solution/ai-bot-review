# Ad Serving Backend (Go) — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của backend ad serving viết bằng Go/Gin. Căn cứ: 📐 Coding Standards — Backend Go/Gin v1.0.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.

## 1. Tổng quan
Backend phân giải cấu hình ad unit theo tag ID, áp dụng targeting/frequency/blocklist và đẩy event sang Kafka. Một module, hai binary:
- `cmd/api`: HTTP API server (Gin).
- `cmd/worker`: Asynq worker (hiện xử lý rebuild bloom filter URL blacklist).
Stack: Gin · MongoDB · Redis (qua Sentinel) · Kafka · Asynq · Google Wire. Lệnh: `wire ./cmd/api/`, `wire ./cmd/worker/`, `gofmt -l .`, `go vet ./...`, `go test ./...`.

## 2. Cấu trúc thư mục & trách nhiệm
- `cmd/<app>/wire.go`: danh sách provider (`//go:build wireinject`), nguồn sự thật cho DI. `wire_gen.go`: sinh tự động, KHÔNG sửa tay. `server.go`: struct `Server` với `Start/Stop/Run`, giữ các client dài hạn (Redis, Kafka, Asynq, Mongo) và đóng chúng khi shutdown. `main.go`: load config, logger, `Initialize<App>()`.
- `internal/app/api/v{N}/`: mỗi version là một lát dọc tự chứa — `binding/` (DTO request/response), `validation/` (validate + parse query → metadata có kiểu), `controller/` (handler Gin mỏng), `service/` (nghiệp vụ của version đó).
  - `v1`: tracking event ad unit (`POST /v1/adUnits/events`) — legacy.
  - `v3`: viewability (`GET /v3/viewAbility/...`).
  - `v4`: phân giải ad unit config (`GET /v4/config/adUnitConfig/:tagId`, `.../passback/:tagId`) — nơi phát triển chính.
  - `system`: health check, trigger rebuild bloom filter.
- `internal/app/api/router/`: `base_router.go` gắn middleware toàn cục và mount `RouterV1/V3/V4` (mỗi version một file `router_v{N}.go`).
- Dùng chung giữa các version: `internal/binding/` (DTO domain, payload Kafka), `internal/config/constant/` (mã lỗi, tên task Asynq, topic), `internal/service/` (cache, Kafka), `internal/infrastructure/` (client Redis/Kafka/Mongo/Asynq), `internal/repository/` (truy cập Mongo), `internal/common/` (`api_response`, `NewAPIError`).
- `internal/app/worker/`: handler → service → repository, keyed theo tên task Asynq; `service.go` đăng ký handler vào `asynq.ServeMux`.
- `internal/config/config.go`: đọc env bằng `caarlos0/env` (tag `,required`) + `godotenv`. Biến bắt buộc: `ENV`, `APP_NAME`, `HOST`, `LOG_LEVEL`, `LOG_JSON`, `SENTINEL_LIST`, `SENTINEL_NAME`, `KAFKA_BROKERS`. `ENV == "production"` bật Gin release mode.

## 3. Luật review

### 3.1. Ranh giới tầng — `router → middleware → controller (bind + validate) → service → repository → MongoDB`
- [chặn merge] Service hoặc repository nhận `*gin.Context`/import `gin`.
- [chặn merge] Controller hoặc service gọi trực tiếp driver Mongo/Redis/Kafka thay vì qua repository/`internal/service` hạ tầng.
- [chặn merge] Sửa tay `cmd/<app>/wire_gen.go` (diff đổi `wire_gen.go` mà không đổi `wire.go`).
- [cảnh báo] Controller chứa logic nghiệp vụ (tính toán, gọi nhiều service, quyết định targeting).
- [cảnh báo] Version mới hoặc API mới import chéo `service/` của version khác thay vì đưa phần dùng chung lên `internal/service/` hoặc `internal/binding/`.
- [cảnh báo] Provider mới (controller/service/validation/repository) không được thêm vào `wire.Build(...)` — CHỈ báo khi diff có sửa `wire.go` mà thiếu provider đó.

### 3.2. Request, validate, response
- [cảnh báo] DTO request mới không đặt trong `binding/` của version (hoặc `internal/binding/` nếu dùng chung); bind không dùng `ShouldBind*`.
- [cảnh báo] Validate/parse query viết trong controller thay vì `validation/`.
- [cảnh báo] Response không đi qua `common/api_response`; lỗi nghiệp vụ không dùng `common.NewAPIError(constant.ErrX)`; mã lỗi mới không thêm vào `config/constant/error_code.go`.
- [cảnh báo] Đổi shape response của `v1`/`v3`/`v4` đang dùng (field, kiểu, status) — contract với ad tag phía trình duyệt.

### 3.3. Lỗi, context, concurrency
- [chặn merge] `panic` trong luồng request/job (recovery middleware chỉ là lưới an toàn).
- [chặn merge] Goroutine mới không dừng theo `ctx.Done()`/shutdown.
- [cảnh báo] Không bọc lỗi bằng `%w`; so sánh lỗi bằng chuỗi.
- [cảnh báo] Hàm I/O mới không nhận `context.Context` làm tham số đầu; dùng `context.Background()` giữa luồng request.
- [cảnh báo] Client/consumer mới không được đóng trong `Server.Stop`.

### 3.4. Worker, Kafka, Redis
- [cảnh báo] Task Asynq mới: tên không định nghĩa trong `internal/config/constant/asynq.go`; handler không đặt trong `internal/app/worker/handler/` hoặc không đăng ký trong mux của `service.go`; provider không thêm vào `cmd/worker/wire.go` — CHỈ báo phần xác minh được.
- [cảnh báo] Task/consumer không idempotent; `Enqueue` không cấu hình `MaxRetry`.
- [cảnh báo] Topic Kafka là chuỗi literal thay vì hằng trong `constant/`.
- [cảnh báo] Kết nối Redis kiểu `host:port` trực tiếp thay vì Sentinel (`SENTINEL_LIST`, `SENTINEL_NAME`).

### 3.5. Cấu hình & log
- [cảnh báo] Biến môi trường mới không khai báo trong struct `config.go` (với `,required` nếu bắt buộc) và `.env.example`.
- [cảnh báo] `os.Getenv` rải rác; `fmt.Println`/`log.Print*` thay vì logger của dự án.
- [nit] Symbol exported mới thiếu GoDoc.

### 3.6. Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.
- [cảnh báo] Sửa logic phân giải config `v4` (targeting, frequency, blocklist, passback) mà PR không có test cho nhánh thay đổi — CHỈ khi thay đổi đổi hành vi (thêm/sửa nhánh, điều kiện, ngưỡng, kết quả) VÀ PR không thêm/sửa case test nào cho phần đó VÀ (nếu đọc được repo) test hiện có chưa kiểm hành vi mới; refactor không đổi hành vi thì KHÔNG báo.
- [nit] Test controller version mới không dùng `httptest` + `gin.TestMode` qua router của version đó.

## 4. Quy ước đặt tên
- [nit] File `snake_case.go`; package chữ thường không gạch dưới; constructor `NewXxx`; viết tắt đúng chữ hoa (`ID`, `URL`, `HTTP`).
- [nit] Router version mới đặt tên `router_v{N}.go`, struct `RouterV{N}`.

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- `v1` là API legacy: không đề xuất refactor `v1` khi PR không yêu cầu.
- Gin default logger tắt ở production (có middleware logger riêng) — không báo thiếu logger.

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Thêm version mới: tạo lát `v{N}/{binding,validation,controller,service}`, `router_v{N}.go`, thêm constructor vào `wire.go`, mount trong `base_router.go`, chạy `wire ./cmd/api/`.
- Thêm task: tên trong constant asynq → repository/service → handler → đăng ký mux → provider trong `cmd/worker/wire.go`.
- Ưu tiên thay đổi nhỏ, đúng tầng; không đổi contract response đang chạy.
