# Quy tắc unit test — Go/Gin (testing + testify + mockery)
Nguồn: [TECH] Test Standard — Backend Go/Gin v1.0. Bổ sung cho mục Test trong `core.md`. KHÔNG áp dụng khi luật dự án ghi dự án chưa có test framework.

Bối cảnh chuẩn: `*_test.go` đặt CẠNH file source, CÙNG package; mock sinh bằng mockery (khai báo trong `.mockery.yaml`, đặt ở `mocks/`) hoặc viết tay; integration test tách bằng `//go:build integration`. Coverage tối thiểu: toàn service 75% · `internal/service` 85% · controller/handler 70%; chạy `go test ./... -race`.

## Thiếu test (§3.2, §7.1)
- [cảnh báo] Hàm/method MỚI trong `internal/service/`, util có nhánh rẽ trong `internal/utils/`, custom validator, handler worker (Asynq) mà PR không có `*_test.go` tương ứng — CHỈ khi xác minh được danh sách file của PR; không xác minh được thì hỏi.
- [nit] Test có trong diff nhưng thiếu case tối thiểu (CHỈ khi nhìn thấy toàn bộ test của đơn vị đó):
  - Service: happy path; lỗi nghiệp vụ → `*APIError` đúng `constant.ErrX`; lỗi kỹ thuật từ repo được bọc `%w` và `errors.Is` khớp; verify repo gọi đúng tham số (`mock.Anything` cho ctx).
  - Controller Gin: bind fail → 422 + envelope lỗi đúng shape; service trả `*APIError` → đúng HTTP status; thành công → envelope `{success: true, data}`.
  - Util: happy path; biên (chuỗi rỗng, 0, nil slice/map, giá trị cực đại); input sai trả error.
  - Custom validator: giá trị hợp lệ pass; MỖI kiểu giá trị không hợp lệ một case.
  - Worker handler: payload hợp lệ → gọi đúng service; payload hỏng → trả error để Asynq retry; idempotent.
  - Hàm có concurrency: đúng khi chạy song song; goroutine dừng theo ctx.

## Cô lập & mock (§2.5, §3.2)
- [cảnh báo] Unit test (không có build tag `integration`) kết nối Mongo/Kafka/Redis thật hoặc gọi HTTP ngoài thật.
- [cảnh báo] File integration test (`*_integration_test.go`) thiếu `//go:build integration`.
- [cảnh báo] Sửa tay file mock do mockery sinh (diff đổi `mocks/*.go` mà không đổi interface/`.mockery.yaml`).
- [cảnh báo] Test logic phụ thuộc thời gian dùng `time.Now()` thật thay vì clock inject/cố định; dùng `time.Sleep` để chờ goroutine.
- [nit] Thêm thư viện mock/assert khác (gomock, ginkgo/gomega...) — chuẩn chỉ dùng testify + mockery; `mockery`/`golangci-lint` thêm vào `go.mod` thay vì cài binary.

## Viết test (§3.4)
- [cảnh báo] So khớp lỗi bằng chuỗi (`err.Error() == ...`, `assert.EqualError`, `strings.Contains(err.Error(), ...)`) thay vì `errors.Is`/`errors.As`/`assert.ErrorIs` — trừ khi chính message là hành vi cần kiểm.
- [cảnh báo] Dùng `assert` cho điều kiện tiên quyết rồi dùng tiếp kết quả (ví dụ `assert.NoError(t, err)` rồi truy cập `got.Field` có thể nil) — dùng `require`.
- [cảnh báo] `t.Parallel()` trong subtest dùng biến vòng lặp mà không capture (`tt := tt`) khi module dùng Go < 1.22, hoặc subtest song song dùng chung mock/state có thể bị sửa.
- [cảnh báo] Test controller Gin không `gin.SetMode(gin.TestMode)` hoặc dựng server thật thay vì `httptest`.
- [cảnh báo] Mock mockery tạo bằng `&mocks.X{}` mà không gọi `AssertExpectations(t)` (nên dùng `mocks.NewX(t)`).
- [nit] Nhiều trường hợp cho cùng một hàm viết thành nhiều hàm test lặp thay vì table-driven với `t.Run(name, ...)` (Coding Standards §13 — BẮT BUỘC table-driven khi có nhiều case).
- [nit] Tên hàm test không theo `TestXxx`/tên subtest không mô tả hành vi; file test khác package với source khi cần truy cập unexported.

## Cấu hình — CHỈ áp dụng khi diff có workflow CI, `Makefile`, `.golangci.yml`, `.mockery.yaml`
- [cảnh báo] Bỏ `-race` khỏi lệnh test; hạ ngưỡng coverage trong CI dưới 75%; bỏ bước `gofmt`/`golangci-lint`.
