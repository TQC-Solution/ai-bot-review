# Quy tắc Node.js backend — chung cho các dự án Node
Nguồn: Coding Standards CORE §5–§7 + BE Express §8–§10 (phần không phụ thuộc khuôn base-backend). Khuôn riêng (`res.sendJson`, `CustomError`, Biz/Repo, EventBus, Bull) nằm trong luật của từng dự án.
(Bản sao giống hệt: `backend-node/node.md` và `expressjs/node.md`; sửa một chỗ thì đồng bộ chỗ còn lại.)

## Async & xử lý lỗi
- [chặn merge] Promise không được `await`/`.catch()` ở nơi lỗi sẽ thành unhandled rejection (gọi hàm async trong event handler, callback, `setTimeout`, `forEach(async ...)`) — CHỈ khi toàn bộ đoạn code hiện trong diff. [📐 Core §1.2]
- [chặn merge] Handler async của Express (route/middleware) MỚI không chuyển lỗi về `next(error)` hoặc không bọc try/catch, khi dự án không dùng `express-async-errors` hay wrapper async — CHỈ khi xác minh được dự án không có cơ chế đó (xem luật dự án). [📐 BE §3.3; BE §2]
- [cảnh báo] Thao tác I/O đồng bộ (`fs.readFileSync`, `execSync`, `crypto.pbkdf2Sync`, vòng lặp nặng) trong luồng xử lý request. [📐 BE §4.1]
- [cảnh báo] `forEach(async ...)` hoặc `map(async ...)` mà không `await Promise.all(...)`. [📐 Core §1.2]
- [nit] Gọi tuần tự nhiều tác vụ độc lập bằng `for ... await` khi có thể `Promise.all` — chỉ khi số phần tử có thể lớn. [Dự án]

## Bảo mật & HTTP
- [chặn merge] Query MongoDB nhận nguyên object từ `req.body`/`req.query` (rủi ro NoSQL injection như `{ $gt: '' }`) mà không validate/ép kiểu. [📐 BE §10; Core §5]
- [cảnh báo] JWT ký mới không có `expiresIn`; verify token không chỉ định thuật toán khi dùng khoá bất đối xứng. [📐 BE §10]
- [cảnh báo] CORS `origin: '*'` kèm `credentials: true`, hoặc cho API cần bảo vệ. [📐 BE §10]
- [cảnh báo] Endpoint công khai nhạy cảm MỚI (login, register, forgot-password, gửi OTP) không có rate limit — viết dạng câu hỏi nếu không xác minh được middleware toàn cục. [📐 BE §10]

## Cấu hình & bí mật
- [cảnh báo] Đọc `process.env.X` trực tiếp ngoài module cấu hình của dự án. [📐 BE §9.2]
- [cảnh báo] Thêm biến môi trường mới mà không thêm vào `.env.example` — CHỈ báo khi đã xác minh `.env.example` không có trong PR; nếu không xác minh được thì hỏi. [📐 BE §9.2; Core §9]
- [cảnh báo] Tự tạo kết nối DB/Redis/queue ngoài module hạ tầng của dự án; resource mới không được đóng khi graceful shutdown. [📐 BE §9.2]

## Worker / queue / consumer
- [cảnh báo] Job hoặc consumer mới không idempotent nhìn thấy được (ghi/cộng dồn dữ liệu mà không kiểm tra đã xử lý chưa). [📐 BE §8]
- [cảnh báo] Payload job/message chứa nguyên object lớn hoặc instance ORM thay vì id. [📐 BE §8]
- [cảnh báo] Tên queue/topic là chuỗi literal rải rác thay vì hằng số tập trung. [📐 BE §8]

## Dữ liệu
- [chặn merge] `sequelize.sync({ alter })` / `sync({ force })` / `synchronize: true` (TypeORM) trong code chạy ở môi trường thật. [📐 BE §6.2]
- [chặn merge] Migration mới thiếu hàm `down`. [📐 BE §6.2]
- [cảnh báo] Ghi nhiều bảng/collection liên tiếp mà một bước lỗi sẽ để dữ liệu nửa vời, không dùng transaction. [📐 BE §6.2]

## package.json — CHỈ áp dụng khi diff có file `package.json`
- [cảnh báo] Dependency MỚI THÊM thuộc nhóm build/test/lint/types (`typescript`, `jest`, `ts-jest`, `@types/*`, `eslint*`, `prettier`, `nodemon`, `ts-node-dev`) đặt trong `dependencies` thay vì `devDependencies`. Không báo nếu dự án build trong môi trường production (Dockerfile cài production rồi mới chạy `tsc`) — không chắc thì hỏi. [📐 BE §12.4]
- [nit] Dependency mới trùng chức năng với thư viện dự án đã có (ví dụ thêm `moment` khi đã có `dayjs`). [Dự án]
- KHÔNG báo về lockfile trừ khi xác minh được PR đổi dependency mà không có `yarn.lock`/`package-lock.json`/`pnpm-lock.yaml`.
- Mục `peerDependencies` CHỈ áp dụng cho thư viện/SDK, không áp dụng cho backend service.
