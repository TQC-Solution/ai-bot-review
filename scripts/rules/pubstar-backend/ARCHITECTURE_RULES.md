# PubStar Backend - Architecture Rules

Tài liệu này mô tả nhanh cấu trúc và quy ước nhẹ cho dự án `pubstar-backend`.
Mục đích: giúp AI và Developer hiểu vị trí code, sửa đúng nơi, không tạo rule quá chặt gây khó phát triển.

## 1. Tổng quan dự án

`pubstar-backend` là backend TypeScript dùng Express, MongoDB/Mongoose, một số module TypeORM cho log/report, Redis/Bull, cron/worker và Swagger.

Các khu vực chính:

* `/src/index.ts`: Entry point chính của API server.
* `/src/api`: Tầng HTTP/API, gồm router, controller, validator, schema/path Swagger theo từng domain.
* `/src/api/router.ts`: Nơi mount các route chính như auth, users, apps, ad-units, reports, payment, network, seller, logs.
* `/src/biz`: Logic nghiệp vụ theo domain, gồm model Mongoose, repository, mapper, type và service nội bộ.
* `/src/common`: Code dùng chung như plugin, interface, middleware/helper chung.
* `/src/config`: Cấu hình môi trường, swagger, job, error.
* `/src/services`: Tích hợp dịch vụ bên ngoài như GAM, Cloudflare, Telegram.
* `/src/jobs`, `/src/workers`, `/src/cronjobs`: Tác vụ nền, queue và cron job.
* `/src/migrations`, `/src/*typeorm.config.ts`: Migration và config TypeORM cho các phần dùng PostgreSQL/log.
* `/src/tools`, `/src/scripts`, `/src/syncs`: Script vận hành, migration helper, sync/tool nội bộ.
* `/src/docs`, `/src/emails`: Tài liệu API/email template hoặc resource liên quan.

## 2. Quy tắc làm việc đơn giản

1. **Giữ đúng tầng:** Route khai báo endpoint/middleware; controller xử lý request/response; validator kiểm tra input; `biz` chứa logic nghiệp vụ/model/repo.
2. **Không làm rule quá chặt:** Ưu tiên theo pattern hiện có của domain gần nhất. Không ép tách service/repository nếu thay đổi nhỏ và code hiện tại chưa theo pattern đó.
3. **Auth & permission:** Khi thêm/sửa API trong `/src/api`, kiểm tra `AuthMiddleware.requireAuth`, `authorization`, role và permission tương tự route cùng domain.
4. **Validation:** Với endpoint nhận input, ưu tiên dùng `express-validation` và validator hiện có. Không bỏ validation cũ khi refactor.
5. **Database:** Với MongoDB, dùng model/type/repo trong `/src/biz`. Với module log/report dùng TypeORM, kiểm tra đúng config/migration tương ứng trước khi sửa schema.
6. **Response & error:** Giữ format response/error đang dùng trong controller/middleware cùng domain. Không tự tạo format mới nếu không cần.
7. **Swagger/OpenAPI:** Khi thêm hoặc đổi API public cho web dùng, cập nhật schema/path/swagger liên quan nếu domain đó đang có tài liệu.
8. **Config & secret:** Không hard-code URL, token, credential. Đọc từ `/src/config/environment.ts` hoặc biến môi trường theo pattern hiện có.
9. **Job/worker/cron:** Khi sửa tác vụ nền, chú ý idempotency và tránh tạo side effect lặp ngoài ý muốn.
10. **Trước khi sửa lớn:** Nếu thay đổi ảnh hưởng auth, permission, payment, report, migration hoặc API contract cho web, hãy đọc kỹ luồng liên quan và xác nhận phạm vi trước.

## 3. Nguyên tắc refactor cho AI

* Bảo toàn endpoint, method, request/response shape nếu không được yêu cầu đổi.
* Không đổi tên collection/model/field database khi chưa có migration và xác nhận ảnh hưởng.
* Không thêm dependency mới nếu có thể dùng thư viện đang có.
* Ưu tiên thay đổi nhỏ, dễ review, đúng mục tiêu.
