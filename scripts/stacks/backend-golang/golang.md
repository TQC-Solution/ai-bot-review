# Quy tắc Go backend (Gin) — chung cho các dự án Go
Nguồn: Coding Standards — Backend Go/Gin v1.0 + CORE. Đường dẫn package (`internal/app/api/...`, `internal/repository`...) có thể khác giữa các dự án; luật dự án mô tả cấu trúc cụ thể.

## Ranh giới tầng & DI
- [chặn merge] Phụ thuộc sai chiều: repository import service/app; service import controller/router; controller gọi thẳng repository/driver DB/Redis/Kafka; hoặc tạo import cycle. [📐 Go §1; Go §2]
- [chặn merge] Service/repository nhận `*gin.Context` hoặc import `gin`. Service nhận `context.Context`; chỉ controller/middleware làm việc với Gin. [📐 Go §2]
- [chặn merge] Sửa tay `wire_gen.go` (diff đổi `wire_gen.go` mà không đổi `wire.go`/provider tương ứng). [📐 Go §2.1]
- [cảnh báo] Controller chứa logic nghiệp vụ thay vì bind → validate → gọi service → trả response. [📐 Go §3.3]
- [cảnh báo] Import driver Mongo/pgx/Redis ngoài tầng repository/infrastructure. [📐 Go §4.2]
- [cảnh báo] Đọc body thô (`ioutil.ReadAll(c.Request.Body)`, `GetRawData`) thay vì `ShouldBind*` vào DTO, khi không có lý do rõ (ví dụ verify chữ ký). [📐 Go §3.1]
- [cảnh báo] Provider mới khởi tạo phụ thuộc thủ công hoặc qua biến toàn cục giữ state thay vì constructor `NewXxx` + Wire; `wire.go` thiếu `//go:build wireinject`. [📐 Go §2.1]

## Lỗi
- [chặn merge] Bỏ qua error trả về (`_ = f()` không comment, hoặc gọi hàm trả error mà không kiểm `err != nil`) trên thao tác I/O/DB. [📐 Go §6]
- [chặn merge] `panic` trong luồng xử lý request/job (chỉ chấp nhận lúc khởi động); `log.Fatal`/`os.Exit` ngoài `main`. [📐 Go §6]
- [cảnh báo] `fmt.Errorf` có `err` nhưng không bọc bằng `%w`; so sánh lỗi bằng chuỗi (`err.Error() == ...`, `strings.Contains(err.Error(), ...)`) thay vì `errors.Is/As`. [📐 Go §6]
- [cảnh báo] Response lỗi/thành công không đi qua helper response chung của dự án; status/message hardcode thay vì mã lỗi định nghĩa trong package constant. [📐 Go §5]
- [nit] Vừa log vừa return cùng một lỗi ở nhiều tầng (log trùng). [📐 Go §6]

## Context & concurrency
- [chặn merge] Goroutine MỚI không có cách dừng (không lắng nghe `ctx.Done()`, không có `WaitGroup`/channel kết thúc) trong process chạy dài → rò rỉ. [📐 Go §7]
- [chặn merge] Ghi map/slice/biến dùng chung từ nhiều goroutine mà không có `sync.Mutex`/`atomic`/channel — CHỈ khi diff cho thấy rõ truy cập đồng thời. [📐 Go §7]
- [cảnh báo] Hàm I/O MỚI không nhận `context.Context` là tham số đầu, hoặc dùng `context.Background()`/`context.TODO()` giữa luồng request thay vì truyền ctx xuống. [📐 Go §7]
- [cảnh báo] Lưu `context.Context` trong struct. [📐 Go §7]
- [cảnh báo] Lời gọi ra ngoài (HTTP, DB, Redis) MỚI không có timeout (`context.WithTimeout` hoặc timeout của client). [📐 Go §7]
- [cảnh báo] `defer` trong vòng lặp dài; tài nguyên (`rows`, `resp.Body`, cursor) không `defer Close()` ngay sau khi mở. [📐 Go §7; Go §12]
- [cảnh báo] Client/consumer/scheduler MỚI không được đóng trong graceful shutdown. [📐 Go §7]

## Job, Kafka, Redis
- [cảnh báo] Tên task Asynq hoặc topic Kafka là chuỗi literal thay vì hằng số trong package constant. [📐 Go §9; Go §10]
- [cảnh báo] Handler task/consumer MỚI không idempotent nhìn thấy được; viết lại logic thay vì gọi service; payload chứa object lớn thay vì id. [📐 Go §9; Go §10]
- [cảnh báo] `Enqueue` không cấu hình `MaxRetry`/`Timeout` khi dự án đã có quy ước. [📐 Go §9]
- [cảnh báo] Producer bỏ qua lỗi gửi; consumer commit offset trước khi xử lý xong. [📐 Go §10]

## Log, cấu hình, bảo mật
- [cảnh báo] `fmt.Println`/`log.Print*` để log thay vì logger có cấu trúc của dự án (logrus/zerolog/zap). [📐 Go §11; Core §7]
- [cảnh báo] Đọc `os.Getenv` rải rác thay vì struct config tập trung; hardcode URI/broker/endpoint. [📐 Go §11; Go §8]
- [chặn merge] Truy vấn ghép chuỗi SQL/Mongo filter từ dữ liệu người dùng. [📐 Go §14; Core §5]

## Quy ước
- [nit] Symbol exported MỚI thiếu GoDoc bắt đầu bằng tên symbol. [📐 Go §12]
- [nit] Viết tắt sai kiểu chữ trong tên (`Url`, `Id`, `Http` thay vì `URL`, `ID`, `HTTP`); tên package có gạch dưới/chữ hoa. [📐 Go §12]
- [nit] Interface định nghĩa ở phía hiện thực thay vì nơi dùng; interface quá lớn. [📐 Go §12]
- Luật về unit test: xem `backend-golang/testing.md`.
