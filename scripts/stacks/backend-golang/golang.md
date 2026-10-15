# Quy tắc Go backend (Gin) — chung cho các dự án Go
Nguồn: Coding Standards — Backend Go/Gin v1.0 + CORE + checklist AI review `REVIEW.go.md` (mục B). Nhãn: [chặn merge] = MUST · [cảnh báo] = SHOULD · [nit] = NOTE. Đường dẫn package (`internal/app/api/...`, `internal/repository`...) có thể khác giữa các dự án; luật dự án mô tả cấu trúc cụ thể.

Luồng chuẩn: `router → middleware → controller (bind + validate) → service → repository → MongoDB`, phụ thuộc MỘT chiều.

## Ranh giới tầng & DI (Go §1–§4)
- [chặn merge] Phụ thuộc sai chiều: repository import service/app; service import app/controller/router; controller import repository/infrastructure; hoặc tạo import cycle.
- [chặn merge] Service/repository nhận `*gin.Context` hoặc import `gin`. Service nhận `context.Context`; chỉ controller/middleware làm việc với Gin.
- [chặn merge] Controller chứa logic nghiệp vụ hoặc gọi thẳng repository/driver DB/Redis/Kafka thay vì bind → validate → gọi service → trả response.
- [chặn merge] Import driver Mongo (hoặc pgx/Redis client) ngoài `internal/repository` và `internal/infrastructure`.
- [chặn merge] Request MỚI không có struct DTO trong `app/api/binding`; đọc body thô (`io.ReadAll(c.Request.Body)`, `GetRawData`) thay vì `ShouldBindJSON`/`ShouldBindQuery` — trừ khi có lý do ghi rõ (ví dụ verify chữ ký); validator tuỳ chỉnh MỚI không đăng ký tập trung ở `app/api/validations`.
- [chặn merge] Sửa tay `wire_gen.go` (diff đổi `wire_gen.go` mà không đổi `wire.go`/provider tương ứng); `wire.go` thiếu `//go:build wireinject`.
- [chặn merge] Provider mới khởi tạo phụ thuộc thủ công, hoặc dùng biến toàn cục giữ state nghiệp vụ, thay vì constructor `NewXxx` + Wire.

## Response & lỗi (Go §5–§6)
- [chặn merge] `c.JSON(...)` với hình dạng khác envelope thay vì `common.RespondOK`/`common.RespondError`; status/message hardcode thay vì `common.NewAPIError(constant.ErrX, cause)`; mã lỗi MỚI không thêm vào `config/constant/error_code.go`.
- [chặn merge] Bỏ qua error trả về (`_ = f()` không có comment giải thích, hoặc gọi hàm trả error mà không kiểm `err != nil`).
- [chặn merge] `fmt.Errorf` có `err` nhưng không bọc bằng `%w`; so sánh lỗi bằng chuỗi (`err.Error() == ...`, `strings.Contains(err.Error(), ...)`) thay vì `errors.Is/As`.
- [chặn merge] `panic` trong luồng xử lý request/job (chỉ chấp nhận lúc khởi động); `log.Fatal`/`os.Exit` ngoài `main`.
- [cảnh báo] Vừa log vừa return cùng một lỗi ở nhiều tầng (chỉ log một lần ở ranh giới).

## Context & concurrency (Go §7)
- [chặn merge] Hàm I/O MỚI không nhận `context.Context` là tham số đầu, hoặc dùng `context.Background()`/`context.TODO()` giữa luồng request thay vì truyền ctx xuống service/repo.
- [chặn merge] Lưu `context.Context` trong struct.
- [chặn merge] Goroutine MỚI không có cách dừng (không lắng nghe `ctx.Done()`, không có `WaitGroup`/channel kết thúc) trong process chạy dài → rò rỉ; scheduler/worker chạy dài không dừng khi shutdown.
- [chặn merge] Ghi map/slice/biến dùng chung từ nhiều goroutine mà không có `sync.Mutex`/`atomic`/channel — CHỈ khi diff cho thấy rõ truy cập đồng thời.
- [chặn merge] Thay đổi code concurrency mà CI/Makefile của repo không chạy `go test -race` — CHỈ khi xác minh được lệnh test; không xác minh được thì hỏi ở mức ⚠️.
- [chặn merge] Client/consumer/goroutine/scheduler MỚI không được đóng trong graceful shutdown (SIGTERM/SIGINT → `server.Shutdown(ctx)` → đóng mongo/redis/kafka/asynq → chờ goroutine).
- [cảnh báo] Lời gọi ra ngoài (HTTP, DB, Redis) MỚI không có timeout (`context.WithTimeout` hoặc timeout của client).
- [cảnh báo] Tài nguyên (`rows`, `resp.Body`, cursor) không `defer Close()` ngay sau khi mở; `defer` trong vòng lặp dài.

## Hạ tầng, job, Kafka (Go §8–§10)
- [chặn merge] Hardcode URI/broker/endpoint/secret; tên task Asynq hoặc topic/consumer group Kafka là chuỗi literal thay vì hằng trong `config/constant` (`asynq.go`, `kafka.go`).
- [chặn merge] Task Asynq MỚI không idempotent, payload là object lớn thay vì id, không validate payload, hoặc handler viết lại logic thay vì gọi service.
- [chặn merge] Consumer Kafka không idempotent hoặc commit offset trước khi xử lý xong; producer bỏ qua lỗi gửi.
- [cảnh báo] `Enqueue` không cấu hình `asynq.MaxRetry`/`asynq.Timeout`.

## Log, cấu hình, bảo mật (Go §11–§13)
- [chặn merge] `fmt.Println`/`log.Print*` để log thay vì logger có cấu trúc `internal/logger` (slog/zap/logrus theo dự án); log PII/GAID/token.
- [chặn merge] Truy vấn ghép chuỗi SQL/Mongo filter từ dữ liệu người dùng (phải dùng `bson`/tham số hoá); thao tác nhạy cảm thiếu kiểm tra quyền ở middleware/service.
- [cảnh báo] Đọc `os.Getenv` rải rác thay vì struct config tập trung ở `internal/config`.
- [cảnh báo] Log thiếu field bối cảnh; luồng request không mang requestId/trace id.

## Quy ước & test (Go §14, §13)
- [chặn merge] Symbol exported MỚI thiếu GoDoc bắt đầu bằng tên symbol.
- [chặn merge] Tên package MỚI có gạch dưới hoặc chữ hoa. (File chưa `gofmt` do CI/`golangci-lint` bắt — chỉ báo khi diff cho thấy rõ.)
- [chặn merge] Service/logic MỚI hoặc bug fix không có test table-driven — điều kiện xác minh theo mục "Về việc THIẾU test" của `core.md` và `backend-golang/testing.md`.
- [cảnh báo] Interface lớn hoặc định nghĩa ở phía hiện thực thay vì nơi dùng; constructor trả interface thay vì struct.
- [cảnh báo] Viết tắt sai kiểu chữ trong tên exported (`Url`, `Id`, `Http` thay vì `URL`, `ID`, `HTTP`); biến toàn cục có thể thay đổi.
- [cảnh báo] Unit test gọi Mongo/Kafka/Redis thật.
- Luật chi tiết về unit test: xem `backend-golang/testing.md`.
