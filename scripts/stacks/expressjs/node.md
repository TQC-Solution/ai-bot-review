# Quy tắc Node.js backend — chung cho các dự án Node
Nguồn: Coding Standards CORE §5–§7 + BE Express §9–§10, §12 + checklist AI review `REVIEW.express.md` (mục C — log, cấu hình, bảo mật, job). Khuôn riêng (`res.sendJson`, `CustomError`, Biz/Repo, EventBus, Bull) nằm trong `expressjs/express.md` và luật của từng dự án.
(Bản sao giống hệt: `backend-node/node.md` và `expressjs/node.md`; sửa một chỗ thì đồng bộ chỗ còn lại.)

## Async & xử lý lỗi
- [chặn merge] Promise không được `await`/`.catch()` ở nơi lỗi sẽ thành unhandled rejection (gọi hàm async trong event handler, callback, `setTimeout`, `forEach(async ...)`) — CHỈ khi toàn bộ đoạn code hiện trong diff.
- [chặn merge] Handler async của Express (route/middleware) MỚI không chuyển lỗi về `next(error)` hoặc không bọc try/catch, khi dự án không dùng `express-async-errors` hay wrapper async — CHỈ khi xác minh được dự án không có cơ chế đó (xem luật dự án).
- [cảnh báo] Thao tác I/O đồng bộ (`fs.readFileSync`, `execSync`, `crypto.pbkdf2Sync`, vòng lặp nặng) trong luồng xử lý request.
- [cảnh báo] `forEach(async ...)` hoặc `map(async ...)` mà không `await Promise.all(...)`.
- [cảnh báo] Gọi tuần tự nhiều tác vụ độc lập bằng `for ... await` khi có thể `Promise.all`.

## Log (BE §9)
- [chặn merge] `console.*` trong code production (lint không chặn giúp); import logger dạng named (`import { logger }`) khi dự án dùng default export `import logger from '@common/logger'`.
- [chặn merge] Log body/header/query chưa mask password, `authorization`, token, cookie.

## Bảo mật & HTTP (BE §10)
- [chặn merge] Query MongoDB nhận nguyên object từ `req.body`/`req.query` (rủi ro NoSQL injection như `{ $gt: '' }`) mà không validate/ép kiểu.
- [chặn merge] Lưu mật khẩu chưa băm (bcrypt/argon2 trong biz trước khi gọi repo).
- [chặn merge] JWT ký mới không có `expiresIn`.
- [chặn merge] CORS `origin: '*'` cho API cần bảo vệ, hoặc kèm `credentials: true`.
- [chặn merge] Endpoint công khai nhạy cảm MỚI (login, register, forgot-password, gửi OTP) không có rate limit — xác minh middleware toàn cục trước khi báo; không xác minh được thì hỏi ở mức ⚠️.
- [cảnh báo] Verify JWT không chỉ định thuật toán khi dùng khoá bất đối xứng.

## Cấu hình & kết nối (BE §10)
- [chặn merge] Đọc `process.env.X` trực tiếp ngoài module cấu hình của dự án (`config/environment.ts` hoặc tương đương).
- [chặn merge] Thêm biến môi trường mới mà không thêm vào module cấu hình VÀ `.env.example` — CHỈ báo khi đã xác minh `.env.example` không có trong PR; không xác minh được thì hỏi.
- [chặn merge] Tự tạo kết nối DB/Redis/queue (`new Sequelize`, `new Redis`, `mongoose.connect`) ngoài module hạ tầng của dự án; resource MỚI không có bước đóng trong graceful shutdown.

## Worker / queue / consumer (BE §8)
- [chặn merge] Job hoặc consumer mới không idempotent nhìn thấy được (ghi/cộng dồn dữ liệu mà không kiểm tra đã xử lý chưa).
- [chặn merge] Payload job/message chứa nguyên object lớn hoặc instance ORM thay vì id; handler viết lại logic thay vì gọi tầng biz.
- [chặn merge] Tên queue/topic là chuỗi literal rải rác thay vì hằng số tập trung.

## Dữ liệu (BE §6)
- [chặn merge] `sequelize.sync({ alter })` / `sync({ force })` / `synchronize: true` (TypeORM) trong code chạy ở môi trường thật.
- [chặn merge] Migration mới thiếu hàm `down`.
- [chặn merge] Ghi nhiều bảng/collection liên tiếp mà một bước lỗi sẽ để dữ liệu nửa vời, không dùng transaction.

## package.json — CHỈ áp dụng khi diff có file `package.json`
- [cảnh báo] Dependency MỚI THÊM thuộc nhóm build/test/lint/types (`typescript`, `jest`, `ts-jest`, `@types/*`, `eslint*`, `prettier`, `nodemon`, `ts-node-dev`) đặt trong `dependencies` thay vì `devDependencies`. Không báo nếu dự án build trong môi trường production (Dockerfile cài production rồi mới chạy `tsc`) — không chắc thì hỏi.
- [nit] Dependency mới trùng chức năng với thư viện dự án đã có (ví dụ thêm `moment` khi đã có `dayjs`).
- KHÔNG báo về lockfile trừ khi xác minh được PR đổi dependency mà không có `yarn.lock`/`package-lock.json`/`pnpm-lock.yaml`.
- Mục `peerDependencies` CHỈ áp dụng cho thư viện/SDK, không áp dụng cho backend service.
