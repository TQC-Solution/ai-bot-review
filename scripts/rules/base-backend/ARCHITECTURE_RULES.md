# Base Backend - Architecture Rules

Tài liệu này mô tả cấu trúc và quy ước của dự án `base-backend`.
Mục đích: giúp AI và Developer hiểu vị trí code, review/sửa đúng nơi, giữ đúng pattern hiện có; không tạo rule quá chặt gây khó phát triển.

## 1. Tổng quan dự án

`base-backend` là backend TypeScript (chế độ `strict: true`) dùng **Express 4**, hỗ trợ **đồng thời MongoDB (Mongoose) và PostgreSQL (Sequelize)**, kèm **Redis/Bull** cho queue/worker, **JWT** cho auth, **winston** cho log và **express-validation (Joi)** cho validate input.

Có nhiều entry point:
- `src/index.ts`: API server (HTTP).
- `src/index-worker.ts`: tiến trình worker xử lý queue/job nền.

Dùng **path alias** (khai báo trong `tsconfig.json`), khi review/sửa import phải tôn trọng alias thay vì đường dẫn tương đối dài:
`@api/*`, `@worker/*`, `@consumer/*`, `@biz/*`, `@common/*`, `@config/*`, `@services/*`.

## 2. Cấu trúc thư mục & trách nhiệm từng tầng

### `src/api` — Tầng HTTP/API (Presentation)
Tổ chức theo từng domain (`user`, `sample`, ...). Mỗi domain gồm bộ 3 file:
- `*.route.ts`: khai báo endpoint, gắn middleware và `validate(schema)`, trỏ tới controller. KHÔNG chứa logic nghiệp vụ.
- `*.controller.ts`: nhận `req`/`res`, ép kiểu body sang DTO, gọi tầng `@biz`, trả response qua `res.sendJson(...)`. Controller phải **mỏng** và luôn bọc `try/catch` rồi `next(error)`.
- `*.validator.ts`: định nghĩa schema Joi (`express-validation`) cho `body`/`query`/`params`.
- `router.ts`: mount toàn bộ route domain.
- `application.ts` / `server.ts`: khởi tạo app Express, middleware chung, error handler.
- `response.middleware.ts`: `ResponseMiddleware.converter` + `handler` xử lý lỗi tập trung; `notFound` cho 404.
- `auth/`: `auth.middleware.ts` (`AuthMiddleware.requireAuth`, `optionalAuth`) và `auth.type.ts`.

### `src/biz` — Tầng nghiệp vụ (Business/Domain)
Tổ chức theo domain, chứa toàn bộ logic và truy cập dữ liệu:
- `*.biz.ts`: logic nghiệp vụ chính (kiểm tra tồn tại, dựng model, gọi repo, emit event, ký JWT...). Đây là nơi đặt business rule.
- `User.ts` (PascalCase): Mongoose schema/model (default export viết HOA, ví dụ `USER`), kèm interface document.
- `*.model.ts`: Sequelize model cho PostgreSQL (class kế thừa `Model`, có getter `transform`, cột `underscored`).
- `*.repo.ts` / `*-postgres.repo.ts`: lớp truy cập DB (Repository). CHỈ nơi này được gọi trực tiếp Mongoose/Sequelize.
- `*.mapper.ts`: chuyển đổi giữa body ↔ schema ↔ response (ví dụ loại bỏ `password` khỏi response).
- `*.type.ts`: interface (tiền tố `I`, ví dụ `IUser`, `IResigterBody`) và enum (tiền tố `E`, ví dụ `EUserRole`, `EUserStatus`).
- `*.event.ts`: hằng số tên event (ví dụ `EVENT_USER_REGISTERED`).
- `*.service.ts`, `*.request.ts`: service nội bộ / kiểu request bổ trợ theo domain.

### `src/common` — Hạ tầng & code dùng chung
- `error/`: `APIError` (có `status`, `errorCode`, `errors`, `stack`), `CustomError` (`CustomError.CustomMessage(...)`).
- `eventbus.ts`: `EventBus.emit(...)` cho side effect bất đồng bộ (decoupling).
- `jwt.ts`: helper `Jwt.sign` / `Jwt.verify`.
- `logger.ts`: winston logger (dùng `logger.error/info`, KHÔNG `console.log`).
- `message.response.ts`: hằng số message (UPPER_SNAKE_CASE, ví dụ `EMAIL_ALREADY_EXISTS`, `UNAUTHORIZED`).
- `infrastructure/`: adapter kết nối `mongo.adapter.ts`, `postgres.adapter.ts`, `redis.adapter.ts`.
- `queue/queue.service.ts`: service cho Bull queue.
- `plugins/pagination/`: plugin phân trang dùng chung.
- `response.interface.ts`, `timestamp.interface.ts`, `tracking/`: interface và tracking dùng chung.

### `src/config` — Cấu hình
- `environment.ts`: đọc TẤT CẢ biến môi trường (qua `dotenv-safe`) và export thành hằng số có kiểu (`PORT`, `JWT_SECRET`, `MONGODB_URI`, `DB_*_POSTGRES`...). Mọi config phải lấy từ đây.
- `db.ts`, `jobs.ts`, `errors.ts` (`ErrorCode`).

### `src/worker` — Tác vụ nền
- `application.ts`, `server.ts`, `router.ts`, `interface.ts` và các job theo domain (`sample/sample.job.ts`, `sample/sample-repeater.job.ts`).

### `src/migrations` — Migration Sequelize (PostgreSQL)
File migration `*.js` chạy qua `sequelize-cli`.

## 3. Quy tắc làm việc & dependency

1. **Giữ đúng tầng:** `route → controller → biz → repo → model`. KHÔNG gọi DB (Mongoose/Sequelize) trực tiếp trong controller; KHÔNG đặt business logic trong route/controller. Controller không tự build query.
2. **Validate input:** endpoint nhận input phải có schema Joi trong `*.validator.ts` và mount qua `validate(...)` ở route. Không bỏ validation khi refactor.
3. **Auth & permission:** API cần bảo vệ phải gắn `AuthMiddleware.requireAuth`; lấy user qua `req.userId` đã set sẵn. Theo pattern route cùng domain.
4. **Xử lý lỗi nhất quán:** ném `APIError`/`CustomError` thay vì trả lỗi thủ công; để `ResponseMiddleware` xử lý tập trung. Giữ format response lỗi `{ error_code, message, stack, errors }` (stack/errors chỉ lộ ở `development`). Controller luôn `try/catch` + `next(error)`.
5. **Hai nguồn DB:** phân biệt rõ MongoDB (Mongoose, model `User.ts`, repo `*.repo.ts`) và PostgreSQL (Sequelize, `*.model.ts`, repo `*-postgres.repo.ts`). Khi đổi schema PostgreSQL phải có migration tương ứng trong `src/migrations`.
6. **Mapper cho response:** dùng `*.mapper.ts` để biến đổi dữ liệu trả ra (đặc biệt loại bỏ field nhạy cảm như `password`). Không trả thẳng document DB ra client.
7. **Side effect qua EventBus:** thao tác phụ (gửi mail, tracking...) nên `EventBus.emit(...)` thay vì nhồi vào luồng chính.
8. **Config & secret:** KHÔNG hard-code URL/token/credential. Đọc từ `@config/environment`. Bí mật (JWT, DB password) chỉ ở server, không log ra ngoài.
9. **Logging:** dùng `@common/logger` (winston), không `console.log` trong code chạy thật.
10. **Async an toàn:** mọi `await` phải nằm trong `try/catch` hoặc được controller bắt qua `next(error)`; tránh unhandled promise rejection.
11. **Job/worker:** khi sửa job nền chú ý idempotency, tránh side effect lặp.

## 4. Quy ước đặt tên

- File: `kebab/dot` theo vai trò — `user.controller.ts`, `user.biz.ts`, `user.repo.ts`, `user.type.ts`, `user.event.ts`. Riêng Mongoose model viết PascalCase (`User.ts`).
- Class: PascalCase (`UserController`, `UserBiz`, `UserRepo`), thường dùng **static method**.
- Interface: tiền tố `I` (`IUser`, `IUserResponse`). Enum: tiền tố `E` (`EUserRole`).
- Hằng số message/event: UPPER_SNAKE_CASE (`EMAIL_ALREADY_EXISTS`, `EVENT_USER_REGISTERED`).
- Tôn trọng `tsconfig` strict: cấm `any` tùy tiện, narrow null trước khi dùng, hạn chế `as any` (hiện có vài chỗ ép kiểu — không nhân rộng thêm).

## 5. Nguyên tắc refactor cho AI

- Bảo toàn endpoint, HTTP method và shape request/response nếu không được yêu cầu đổi.
- Không đổi tên collection/model/cột DB khi chưa có migration và xác nhận ảnh hưởng.
- Tuân theo pattern của domain gần nhất (`user`, `sample`) khi thêm domain mới; tạo đủ bộ `route/controller/validator` + `biz/repo/type/mapper`.
- Không thêm dependency mới nếu thư viện hiện có (lodash, dayjs, http-status...) đã đáp ứng.
- Ưu tiên thay đổi nhỏ, dễ review, đúng tầng và đúng mục tiêu.
