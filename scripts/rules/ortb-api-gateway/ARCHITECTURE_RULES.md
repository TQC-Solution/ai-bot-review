# Base Backend — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của dự án `base-backend` (và các dự án fork từ nó). Mục đích: giúp AI và developer đặt code đúng chỗ, giữ đúng pattern; khi review chỉ báo những gì thật sự vi phạm. Căn cứ: 📐 Coding Standards — Backend Node.js/Express v1.0.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.

## 1. Tổng quan
- TypeScript `strict: true`, **Express 4**, **MongoDB (Mongoose 5)** và **PostgreSQL (Sequelize 6)** song song, **Redis/Bull** cho queue, **JWT** cho auth, **winston** cho log, **express-validation 3 + Joi** cho validate.
- Entry point: `src/index.ts` (API) và `src/index-worker.ts` (worker).
- Path alias (khai báo trong `tsconfig.json`): `@api/*`, `@biz/*`, `@common/*`, `@config/*`, `@worker/*`. Hai alias `@consumer/*`, `@services/*` đã khai báo nhưng thư mục chưa tồn tại. KHÔNG có alias `@/*`.

## 2. Cấu trúc thư mục & trách nhiệm
- `src/api/<domain>/`: `*.route.ts` (method + path + middleware, không logic) · `*.validator.ts` (schema Joi cho body/query/params) · `*.controller.ts` (class static, mỏng: đọc req → gọi biz → `res.sendJson`). Ngoài ra: `router.ts` (mount route), `application.ts`/`server.ts` (khởi tạo app, đăng ký event), `response.middleware.ts` (converter → notFound → handler xử lý lỗi tập trung), `auth/auth.middleware.ts` (`AuthMiddleware.requireAuth`, `optionalAuth`).
- `src/biz/<domain>/`: `*.biz.ts` (business rule) · `*.repo.ts` (Mongo) / `*-postgres.repo.ts` (Postgres) — nơi DUY NHẤT gọi Mongoose/Sequelize · `User.ts` (Mongoose model, PascalCase) / `*.model.ts` (Sequelize model) · `*.mapper.ts` (body ↔ schema ↔ response) · `*.type.ts` (interface `I*`, enum `E*`) · `*.event.ts` (hằng số tên event + class `<Domain>Event`).
- `src/common/`: `error/` (`APIError`, `CustomError`) · `eventbus.ts` · `jwt.ts` · `logger.ts` (winston, default export) · `message.response.ts` (hằng số message UPPER_SNAKE) · `infrastructure/` (adapter Mongo/Postgres/Redis, singleton) · `queue/queue.service.ts` · `plugins/pagination/`.
- `src/config/`: `environment.ts` (đọc mọi biến môi trường qua dotenv-safe, export hằng số có kiểu) · `errors.ts` (enum `ErrorCode`) · `jobs.ts` (tên queue) · `db.ts`.
- `src/worker/`: `application.ts`, `server.ts`, `router.ts` (mảng `queues`), `interface.ts` (`JobHandler`), job theo domain `<domain>/*.job.ts`.
- `src/migrations/`: migration Sequelize, JS thuần, chạy bằng `sequelize-cli`.

## 3. Luật review

### 3.1. Ranh giới tầng — `route → AuthMiddleware → validate → controller → biz → repo → model`
- [chặn merge] Controller gọi trực tiếp repo/model/Mongoose/Sequelize, hoặc tự build query. [📐 BE §2]
- [chặn merge] Biz import/nhận `Request`/`Response` của express hoặc gọi `res.status()`/`res.json()`. [📐 BE §2]
- [chặn merge] Trả thẳng document/instance ORM ra client không qua mapper/transform; response chứa `password`. [📐 BE §2; BE §4.3]
- [cảnh báo] Logic nghiệp vụ (điều kiện, tính toán, gọi nhiều repo) nằm trong route/controller. [📐 BE §2; BE §3.3]
- [cảnh báo] Biz `*.biz.ts` MỚI import trực tiếp model/ORM thay vì qua repo. [📐 BE §4.1]
- [cảnh báo] Repo chứa if nghiệp vụ hoặc `throw CustomError/APIError` (repo trả `null`/`false`/`[]`, biz quyết định). [📐 BE §4.2]
- [cảnh báo] Import tương đối xuyên tầng (`../../biz/...`) hoặc dùng alias `@/*`. [📐 BE §1]

### 3.2. Route, validate, controller
- [chặn merge] Method controller MỚI (thân hàm hiện đầy đủ trong diff) có `await` nhưng không bọc `try { ... } catch (error) { next(error) }` — base không có async error handler, thiếu sẽ treo request và có thể làm sập process. [📐 BE §3.3]
- [cảnh báo] Route MỚI nhận body/query/params mà dòng khai báo route không có `validate(...)`. [📐 BE §3.2]
- [cảnh báo] `validate(schema)` thiếu `{ context: true }` (không có thì `.default()` và ép kiểu của Joi không được ghi vào `req`). [📐 BE §3.2]
- [cảnh báo] Dùng `express-validator`, `matchedData`, `validationResult`, hoặc tự viết middleware validate. [📐 BE §3.2]
- [cảnh báo] Lấy id người dùng hiện tại từ body/query thay vì `req.userId`. [📐 BE §3.3]
- [cảnh báo] Endpoint MỚI cần bảo vệ (thao tác dữ liệu của user) mà route không gắn `AuthMiddleware.requireAuth` — hỏi nếu không rõ endpoint có public hay không. [📐 BE §3.1; Core §5]

### 3.3. Response & lỗi
- [cảnh báo] Gọi `res.json()`/`res.send()`/`res.status()` trực tiếp (ngoại lệ: health check `GET /status`). [📐 BE §5.1]
- [cảnh báo] `res.sendJson(...)` truyền array/primitive, truyền 2 tham số, hoặc truyền object không có khoá `data` (field sẽ đổ thẳng vào root envelope). [📐 BE §5.1]
- [cảnh báo] `CustomError.CustomMessage(...)` trong code mới — dùng `CustomError.BadRequest(MESSAGE_CONST, ErrorCode.X)` để client phân biệt được lỗi. [📐 BE §5.2]
- [cảnh báo] errorCode là số trần thay vì `ErrorCode.X`; message là chuỗi viết trực tiếp thay vì hằng số trong `common/message.response.ts`. [📐 BE §5.2; BE §4.1]
- [cảnh báo] Trả lỗi thủ công (`res.status(400).json(...)`) thay vì `throw` để `ResponseMiddleware` xử lý. [📐 BE §5.2]

### 3.4. Dữ liệu
- [chặn merge] Dùng `sequelize.sync({ alter })` / `sync({ force })`. [📐 BE §6.2]
- [chặn merge] Migration mới thiếu hàm `down`. [📐 BE §6.2]
- [cảnh báo] Diff đổi Sequelize model (thêm/xoá cột) mà không có migration trong diff — viết dưới dạng câu hỏi. [📐 BE §6.2]
- [cảnh báo] Thao tác ghi nhiều bảng Postgres liên tiếp không dùng `transaction`. [📐 BE §6.2]
- [cảnh báo] Schema Mongoose mới thiếu `timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }`; model Sequelize mới thiếu `underscored: true`/`timestamps`/`tableName`. [📐 BE §6.1; BE §6.2]
- [nit] Query Mongo chỉ đọc không dùng `.lean()`; API danh sách không dùng plugin `paginate`. [📐 BE §6.1]

### 3.5. EventBus & worker
- [chặn merge] Event handler async MỚI không tự `try/catch` toàn thân hàm (EventBus không bắt lỗi → unhandled rejection làm shutdown process). [📐 BE §7]
- [chặn merge] Job handler MỚI không có `try/catch` hoặc không gọi `done()` khi xong / `done(error)` khi lỗi (job treo ở trạng thái active). [📐 BE §8]
- [cảnh báo] Tên event không theo mẫu `'event.<domain>.<pastTense>'`; `EventBus.on(...)` ngoài file `*.event.ts`. [📐 BE §7]
- [cảnh báo] Emit instance ORM thay vì DTO đã transform. [📐 BE §7]
- [cảnh báo] Dùng EventBus cho việc cần retry/bền vững (gửi email, gọi API ngoài) — nên dùng Bull job. [📐 BE §7; BE §8]
- [cảnh báo] Tên queue là chuỗi literal thay vì hằng số trong `config/jobs.ts`; payload job chứa object lớn thay vì id; job không idempotent. [📐 BE §8]
- [cảnh báo] Class event/job MỚI nhưng diff có sửa `application.ts`/`worker/router.ts` mà không đăng ký class đó. [📐 BE §7; BE §8]

### 3.6. Log, cấu hình, bảo mật
- [chặn merge] Lưu mật khẩu chưa băm (bcrypt/argon2) xuống DB. [📐 BE §10; Core §5]
- [chặn merge] Log `req.body`, header `authorization`, password, token mà không mask. [📐 BE §10; Core §7]
- [cảnh báo] `console.*` trong `src/` (ngoại trừ `src/migrations/`) — dùng `import logger from '@common/logger'`. [📐 BE §9.1]
- [cảnh báo] Import logger dạng named (`import { logger } from '@common/logger'`) — logger là default export. [📐 BE §9.1]
- [cảnh báo] Đọc `process.env.X` ngoài `src/config/`; tự `new Sequelize`/`new Redis`/`mongoose.connect` ngoài `common/infrastructure`. [📐 BE §9.2]
- [cảnh báo] `Jwt.sign(...)` không truyền `expiresIn`. [📐 BE §10]

### 3.7. Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.
- Hai tầng test hợp lệ: API-level `src/api/<domain>/__tests__/<domain>.<endpoint>.test.ts` (supertest, mock biz/repo) và biz-level (gọi thẳng `<Domain>Biz`, mock repo).
- [cảnh báo] Test API mock thẳng Mongoose/Sequelize model thay vì repo (`*.repo.ts`); test biz gọi repo thật. [📐 Test Node §7.1]
- [cảnh báo] Test API không assert envelope `res.sendJson` (`error_code`, `data`) hoặc mã lỗi `ErrorCode.X` của nhánh lỗi. [📐 Test Node §6]
- [nit] Endpoint có `AuthMiddleware.requireAuth` mà test thiếu case không token (401). [📐 Test Node §6]

## 4. Quy ước đặt tên
- [nit] File theo mẫu `<domain>.<layer>.ts` (`user.biz.ts`, `user-postgres.repo.ts`); Mongoose model PascalCase (`User.ts`). Domain MỚI dùng `*.biz.ts` / class `<Domain>Biz`, không tạo thêm `*.service.ts`. [📐 BE §12.2]
- [nit] Class PascalCase với static method (`UserBiz`, `UserRepo`, `UserMapper`); interface tiền tố `I`, enum tiền tố `E`; hằng số message/event UPPER_SNAKE_CASE. [📐 BE §12.2]
- [nit] `export default` chỉ dùng cho router của domain, `logger`, model Mongoose. [📐 BE §12.2]

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
Các điểm dưới đây là hiện trạng của base. Chỉ báo khi code MỚI copy lại đúng pattern này.
- `biz/sample/sample.service.ts` gọi model trực tiếp, không có repo, đặt tên `*.service.ts`.
- `user.mapper.ts` → `toUserResponse` trả cả `password`; `UserBiz`/`UserPostgresRepo` lưu password chưa băm.
- `api/user/user.controller.ts` gọi `res.sendJson(result)` không bọc `data`; còn `req.body as any as IResigterBody`, `req.query as any`.
- `api/user/user.route.ts` gọi `validate(registerPostgres)` thiếu `{ context: true }`.
- `api/sample/sample.controller.ts`, `api/application.ts` còn import tương đối xuyên tầng.
- `AuthMiddleware.requireAuth` chỉ chấp nhận ObjectId (token user Postgres luôn 401); payload JWT lệch khoá `id`/`userId`.
- `config/db.ts` có `console.log` in cả cấu hình DB; `response.middleware.ts` log body + rawHeaders khi lỗi 5xx.
- Chưa có CORS, rate limit, giới hạn body size.

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Giữ nguyên endpoint, HTTP method, shape request/response nếu không được yêu cầu đổi; không đổi tên collection/model/cột khi chưa có migration.
- Domain mới bắt chước domain `user`: đủ `route/validator/controller` + `type/biz/repo/mapper/event/Model`; mount route trong `api/router.ts`, đăng ký event trong `Application.registerEvents()`, job trong `worker/router.ts`, mã lỗi trong `ErrorCode`, message trong `message.response.ts`, biến môi trường trong `config/environment.ts` và `.env.example`.
- Không thêm dependency mới nếu thư viện sẵn có (lodash, dayjs, http-status…) đã đáp ứng. Ưu tiên thay đổi nhỏ, đúng tầng, đúng mục tiêu.
