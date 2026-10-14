# PubStar Backend — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của `pubstar-backend`. Căn cứ: 📐 Coding Standards — Backend Node.js/Express v1.0, áp dụng mức "nhẹ": theo pattern của domain gần nhất, không ép tách service/repository cho thay đổi nhỏ.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.
Response/error format theo pattern hiện có của domain; KHÔNG áp envelope chuẩn mới (`error_code`, `/v2`) cho endpoint cũ hoặc domain đang dùng format khác.

## 1. Tổng quan
TypeScript, Express, MongoDB/Mongoose; TypeORM (PostgreSQL) cho một số module log/report; Redis/Bull, cron/worker; Swagger.

## 2. Cấu trúc thư mục & trách nhiệm
- `src/index.ts`: entry API server.
- `src/api/<domain>`: router, controller, validator, schema/path Swagger. `src/api/router.ts` mount route chính (auth, users, apps, ad-units, reports, payment, network, seller, logs).
- `src/biz/<domain>`: model Mongoose, repository, mapper, type, service nội bộ.
- `src/common`: plugin, interface, middleware/helper chung. `src/config`: environment, swagger, job, error.
- `src/services`: tích hợp ngoài (GAM, Cloudflare, Telegram).
- `src/jobs`, `src/workers`, `src/cronjobs`: tác vụ nền, queue, cron.
- `src/migrations`, `src/*typeorm.config.ts`: migration và config TypeORM.
- `src/tools`, `src/scripts`, `src/syncs`: script vận hành; `src/docs`, `src/emails`: tài liệu, email template.

## 3. Luật review

### 3.1. Auth, quyền, validate
- [chặn merge] Route mới/sửa trong `src/api` thao tác dữ liệu người dùng/admin mà thiếu `AuthMiddleware.requireAuth`/`authorization`/role như route cùng domain.
- [chặn merge] Diff gỡ validation hoặc kiểm tra quyền hiện có mà không thay thế.
- [cảnh báo] Endpoint mới nhận input không dùng `express-validation` + validator như domain cùng loại.

### 3.2. Tầng & dữ liệu
- [cảnh báo] Controller chứa query DB phức tạp hoặc logic nghiệp vụ dài, khi domain đã có repo/service trong `src/biz` — KHÔNG báo nếu domain cũ chưa theo pattern đó và thay đổi nhỏ.
- [chặn merge] Đổi entity TypeORM (cột/bảng) không có migration; `synchronize: true` ở môi trường thật; migration thiếu `down`.
- [cảnh báo] Đổi tên collection/model/field Mongo đang dùng mà PR không có kế hoạch migrate dữ liệu.
- [cảnh báo] Gọi dịch vụ ngoài (GAM, Cloudflare, Telegram) trực tiếp trong controller thay vì `src/services`.

### 3.3. Response, Swagger, vận hành
- [cảnh báo] Response/error mới khác format controller/middleware cùng domain.
- [cảnh báo] API public cho web thêm/đổi mà không cập nhật schema/path Swagger của domain đang có tài liệu — CHỈ khi xác minh được domain có Swagger.
- [cảnh báo] Job/worker/cron mới không idempotent, có thể chạy lặp side effect (gửi email, thanh toán, ghi report).
- [cảnh báo] Thay đổi luồng payment/report mà PR không mô tả phạm vi — dạng câu hỏi.

### 3.4. Cấu hình & bảo mật
- [chặn merge] Hardcode token/credential.
- [cảnh báo] Hardcode URL; đọc `process.env` ngoài `src/config/environment.ts`.

## 4. Quy ước đặt tên
- [nit] Theo pattern file của domain gần nhất.

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- Domain cũ chưa tách service/repository: không yêu cầu tách khi PR chỉ sửa nhỏ.
- Format response khác chuẩn CORE mới: giữ nguyên theo domain.
- (Bổ sung tại đây các mẫu báo sai lặp lại mà dev đã xác nhận.)

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Bảo toàn endpoint, method, request/response shape. Không thêm dependency mới nếu thư viện có sẵn đáp ứng.
- Thay đổi ảnh hưởng auth, permission, payment, report, migration, API contract: đọc kỹ luồng liên quan, xác nhận phạm vi trước.
