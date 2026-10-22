# Quy tắc Express — chung cho các backend Express (JS và TS)
Nguồn: Coding Standards — Backend Node.js/Express v1.0 (phần chung). Khuôn cụ thể của từng dự án (tên helper response, lớp lỗi, alias, EventBus, Bull) nằm trong luật dự án; khi luật dự án mô tả khuôn khác nhưng nhất quán, theo luật dự án.

## Ranh giới tầng — `route → middleware (auth) → validate → controller → service/biz → repository → model`
- [chặn merge] Controller/route MỚI gọi trực tiếp model/ORM (Mongoose, Sequelize, TypeORM) hoặc tự build query, khi dự án có tầng service/repository. [📐 BE §2]
- [chặn merge] Service/biz import hoặc nhận `req`/`res` của Express, hoặc gọi `res.status()`/`res.json()`. [📐 BE §2]
- [chặn merge] Trả thẳng document/instance ORM ra client mà response chứa field nhạy cảm (`password`, token, secret). [📐 BE §2]
- [cảnh báo] Logic nghiệp vụ (điều kiện nhiều nhánh, tính toán, phối hợp nhiều repo) nằm trong route/controller. [📐 BE §3.3]
- [cảnh báo] Repository chứa quyết định nghiệp vụ hoặc ném lỗi nghiệp vụ (repo trả dữ liệu/`null`, tầng nghiệp vụ quyết định). [📐 BE §4.2]
- [cảnh báo] Trả document/instance ORM ra client không qua mapper/transform (khi dự án có mapper). [📐 BE §4.3]

## Route & validate
- [cảnh báo] Route MỚI nhận body/query/params mà không có middleware validate theo thư viện dự án đang dùng (Joi/express-validation, zod...). Xác minh validator chưa được gắn ở router cha trước khi báo. [📐 BE §3.2]
- [cảnh báo] Trộn thư viện validate khác với thư viện dự án đã chọn. [📐 BE §3.2]
- [cảnh báo] Lấy id người dùng hiện tại từ body/query thay vì từ thông tin auth trên `req` (ví dụ `req.userId`, `req.user`). [📐 BE §3.3]
- [cảnh báo] Endpoint MỚI thao tác dữ liệu của người dùng mà route không gắn middleware auth/kiểm quyền như các route cùng domain — viết dạng câu hỏi nếu không rõ endpoint có public hay không. [📐 BE §3.1; Core §5]

## Response & lỗi
- [cảnh báo] Controller tự trả lỗi thủ công (`res.status(400).json(...)`) thay vì `throw`/`next(error)` để error handler tập trung xử lý. [📐 BE §3.3; BE §5.2]
- [cảnh báo] Dùng `res.json()`/`res.send()` trực tiếp khi dự án có helper response chuẩn (xem luật dự án), trừ health check. [📐 BE §5.1]
- [cảnh báo] Error handler trả `error.stack` hoặc message lỗi hệ thống thô ra client ở môi trường production. [📐 BE §5.2; Core §4.1]

## Middleware & app
- [cảnh báo] `express.json()`/`bodyParser` MỚI không đặt `limit`. [📐 BE §10]
- [cảnh báo] Middleware MỚI không gọi `next()` ở mọi nhánh (treo request) — CHỈ khi toàn bộ thân middleware hiện trong diff. [📐 BE §3.1]
- [nit] Middleware dùng chung chứa luật nghiệp vụ của một domain cụ thể. [📐 BE §3.1]
