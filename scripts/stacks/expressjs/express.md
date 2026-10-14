# Quy tắc Express — chung cho các backend Express (JS và TS)
Nguồn: Coding Standards — Backend Node.js/Express v1.0 (phần chung). Khuôn cụ thể của từng dự án (tên helper response, lớp lỗi, alias, EventBus, Bull) nằm trong luật dự án; khi luật dự án mô tả khuôn khác nhưng nhất quán, theo luật dự án.

## Ranh giới tầng — `route → middleware (auth) → validate → controller → service/biz → repository → model`
- [chặn merge] Controller/route MỚI gọi trực tiếp model/ORM (Mongoose, Sequelize, TypeORM) hoặc tự build query, khi dự án có tầng service/repository.
- [chặn merge] Service/biz import hoặc nhận `req`/`res` của Express, hoặc gọi `res.status()`/`res.json()`.
- [chặn merge] Trả thẳng document/instance ORM ra client mà response chứa field nhạy cảm (`password`, token, secret).
- [cảnh báo] Logic nghiệp vụ (điều kiện nhiều nhánh, tính toán, phối hợp nhiều repo) nằm trong route/controller.
- [cảnh báo] Repository chứa quyết định nghiệp vụ hoặc ném lỗi nghiệp vụ (repo trả dữ liệu/`null`, tầng nghiệp vụ quyết định).
- [cảnh báo] Trả document/instance ORM ra client không qua mapper/transform (khi dự án có mapper).

## Route & validate
- [cảnh báo] Route MỚI nhận body/query/params mà không có middleware validate theo thư viện dự án đang dùng (Joi/express-validation, zod...). Xác minh validator chưa được gắn ở router cha trước khi báo.
- [cảnh báo] Trộn thư viện validate khác với thư viện dự án đã chọn.
- [cảnh báo] Lấy id người dùng hiện tại từ body/query thay vì từ thông tin auth trên `req` (ví dụ `req.userId`, `req.user`).
- [cảnh báo] Endpoint MỚI thao tác dữ liệu của người dùng mà route không gắn middleware auth/kiểm quyền như các route cùng domain — viết dạng câu hỏi nếu không rõ endpoint có public hay không.

## Response & lỗi
- [cảnh báo] Controller tự trả lỗi thủ công (`res.status(400).json(...)`) thay vì `throw`/`next(error)` để error handler tập trung xử lý.
- [cảnh báo] Dùng `res.json()`/`res.send()` trực tiếp khi dự án có helper response chuẩn (xem luật dự án), trừ health check.
- [cảnh báo] Error handler trả `error.stack` hoặc message lỗi hệ thống thô ra client ở môi trường production.

## Middleware & app
- [cảnh báo] `express.json()`/`bodyParser` MỚI không đặt `limit`.
- [cảnh báo] Middleware MỚI không gọi `next()` ở mọi nhánh (treo request) — CHỈ khi toàn bộ thân middleware hiện trong diff.
- [nit] Middleware dùng chung chứa luật nghiệp vụ của một domain cụ thể.
