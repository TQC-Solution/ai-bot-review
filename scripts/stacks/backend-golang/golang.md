# Quy tắc Go backend (Gin) — chung cho các dự án Go
Nguồn: Coding Standards — Backend Go/Gin v1.0 + CORE. Đường dẫn package (`internal/app/api/...`, `internal/repository`...) có thể khác giữa các dự án; luật dự án mô tả cấu trúc cụ thể.

## Ranh giới tầng & DI (Go §1–§4)
- [chặn merge] Phụ thuộc sai chiều: repository import service/app; service import controller/router; controller gọi thẳng repository/driver DB/Redis/Kafka; hoặc tạo import cycle.
- [chặn merge] Service/repository nhận `*gin.Context` hoặc import `gin`. Service nhận `context.Context`; chỉ controller/middleware làm việc với Gin.
- [chặn merge] Sửa tay `wire_gen.go` (diff đổi `wire_gen.go` mà không đổi `wire.go`/provider tương ứng).
- [cảnh báo] Controller chứa logic nghiệp vụ thay vì bind → validate → gọi service → trả response.
- [cảnh báo] Import driver Mongo/pgx/Redis ngoài tầng repository/infrastructure.
- [cảnh báo] Đọc body thô (`ioutil.ReadAll(c.Request.Body)`, `GetRawData`) thay vì `ShouldBind*` vào DTO, khi không có lý do rõ (ví dụ verify chữ ký).
- [cảnh báo] Provider mới khởi tạo phụ thuộc thủ công hoặc qua biến toàn cục giữ state thay vì constructor `NewXxx` + Wire; `wire.go` thiếu `//go:build wireinject`.

## Lỗi (Go §5–§6)
- [chặn merge] Bỏ qua error trả về (`_ = f()` không comment, hoặc gọi hàm trả error mà không kiểm `err != nil`) trên thao tác I/O/DB.
- [chặn merge] `panic` trong luồng xử lý request/job (chỉ chấp nhận lúc khởi động); `log.Fatal`/`os.Exit` ngoài `main`.
- [cảnh báo] `fmt.Errorf` có `err` nhưng không bọc bằng `%w`; so sánh lỗi bằng chuỗi (`err.Error() == ...`, `strings.Contains(err.Error(), ...)`) thay vì `errors.Is/As`.
- [cảnh báo] Response lỗi/thành công không đi qua helper response chung của dự án; status/message hardcode thay vì mã lỗi định nghĩa trong package constant.
- [nit] Vừa log vừa return cùng một lỗi ở nhiều tầng (log trùng).

## Context & concurrency (Go §7)
- [chặn merge] Goroutine MỚI không có cách dừng (không lắng nghe `ctx.Done()`, không có `WaitGroup`/channel kết thúc) trong process chạy dài → rò rỉ.
- [chặn merge] Ghi map/slice/biến dùng chung từ nhiều goroutine mà không có `sync.Mutex`/`atomic`/channel — CHỈ khi diff cho thấy rõ truy cập đồng thời.
- [cảnh báo] Hàm I/O MỚI không nhận `context.Context` là tham số đầu, hoặc dùng `context.Background()`/`context.TODO()` giữa luồng request thay vì truyền ctx xuống.
- [cảnh báo] Lưu `context.Context` trong struct.
- [cảnh báo] Lời gọi ra ngoài (HTTP, DB, Redis) MỚI không có timeout (`context.WithTimeout` hoặc timeout của client).
- [cảnh báo] `defer` trong vòng lặp dài; tài nguyên (`rows`, `resp.Body`, cursor) không `defer Close()` ngay sau khi mở.
- [cảnh báo] Client/consumer/scheduler MỚI không được đóng trong graceful shutdown.

## Job, Kafka, Redis (Go §8–§10)
- [cảnh báo] Tên task Asynq hoặc topic Kafka là chuỗi literal thay vì hằng số trong package constant.
- [cảnh báo] Handler task/consumer MỚI không idempotent nhìn thấy được; viết lại logic thay vì gọi service; payload chứa object lớn thay vì id.
- [cảnh báo] `Enqueue` không cấu hình `MaxRetry`/`Timeout` khi dự án đã có quy ước.
- [cảnh báo] Producer bỏ qua lỗi gửi; consumer commit offset trước khi xử lý xong.

## Log, cấu hình, bảo mật (Go §11–§13)
- [cảnh báo] `fmt.Println`/`log.Print*` để log thay vì logger có cấu trúc của dự án (logrus/zerolog/zap).
- [cảnh báo] Đọc `os.Getenv` rải rác thay vì struct config tập trung; hardcode URI/broker/endpoint.
- [chặn merge] Truy vấn ghép chuỗi SQL/Mongo filter từ dữ liệu người dùng.

## Quy ước (Go §14)
- [nit] Symbol exported MỚI thiếu GoDoc bắt đầu bằng tên symbol.
- [nit] Viết tắt sai kiểu chữ trong tên (`Url`, `Id`, `Http` thay vì `URL`, `ID`, `HTTP`); tên package có gạch dưới/chữ hoa.
- [nit] Interface định nghĩa ở phía hiện thực thay vì nơi dùng; interface quá lớn.
- Luật về unit test: xem `backend-golang/testing.md`.
