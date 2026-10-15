# Quy tắc Express — chung cho các backend Express (JS và TS)
Nguồn: Coding Standards — Backend Node.js/Express v1.0 + checklist AI review `REVIEW.express.md` (mục C). Nhãn: [chặn merge] = MUST · [cảnh báo] = SHOULD · [nit] = NOTE.

Repo fork base-backend dùng đúng khuôn dưới đây. Repo KHÔNG fork base-backend (khai báo trong luật dự án hoặc mục "Coding Standards — đặc thù repo" của `CLAUDE.md`): các mục đánh dấu **(khuôn base)** hạ xuống [cảnh báo] nếu repo dùng pattern khác nhưng nhất quán, và theo helper/lớp lỗi/alias thật mà luật dự án mô tả; các mục bảo mật, ranh giới tầng, log, env giữ nguyên nhãn.

Luồng chuẩn: `route → AuthMiddleware.requireAuth → validate(schema, { context: true }) → Controller → Biz → Repo → DB`.

## Ranh giới tầng (BE §2)
- [chặn merge] Controller/route MỚI gọi trực tiếp repo/model/ORM (Mongoose, Sequelize, TypeORM), tự build query, hoặc chứa logic nghiệp vụ (điều kiện nhiều nhánh, tính toán, phối hợp nhiều repo).
- [chặn merge] Biz/service import hoặc nhận `req`/`res` của Express, gọi `res.status()`/`res.json()`, viết query thô, hoặc import model/ORM thay vì repo.
- [chặn merge] Entity/document/instance ORM trả thẳng ra response không qua mapper/transform; DTO response chứa `password`, token, secret.
- [chặn merge] Repo chứa if nghiệp vụ hoặc throw lỗi nghiệp vụ (repo trả dữ liệu/`null`/`false`/`[]`, biz quyết định throw).
- [chặn merge] Import tương đối xuyên tầng (`../../biz/...`); dùng alias `@/*`, hoặc `@consumer/*`/`@services/*` khi thư mục chưa tồn tại. (BE §1)

## Route, validate, controller (BE §3)
- [chặn merge] Endpoint MỚI nhận body/query/params mà không có schema Joi trong `*.validator.ts` — xác minh validator chưa được gắn ở router cha trước khi báo. **(khuôn base)**
- [chặn merge] Dùng `express-validator`/`matchedData`/`validationResult`, hoặc tự viết middleware validate, khi dự án dùng `express-validation` + Joi. **(khuôn base)**
- [chặn merge] `validate(schema)` thiếu `{ context: true }`. **(khuôn base)**
- [chặn merge] Method controller MỚI không bọc `try { ... } catch (error) { next(error) }` khi dự án không có async error handler (treo request, sập process) — CHỈ khi toàn bộ thân method hiện trong diff.
- [chặn merge] Lấy id người dùng hiện tại từ body/query thay vì `req.userId` (hoặc thông tin auth trên `req` mà dự án dùng).
- [cảnh báo] Endpoint MỚI thao tác dữ liệu của người dùng mà route không gắn middleware auth/kiểm quyền như các route cùng domain — viết dạng câu hỏi nếu không rõ endpoint có public hay không.

## Response & lỗi (BE §5)
- [chặn merge] Gọi `res.json()`/`res.send()`/`res.status()` trực tiếp thay vì `res.sendJson` (ngoại lệ: `GET /status`, health check, và endpoint mà giao thức bên ngoài quy định shape). **(khuôn base)**
- [chặn merge] `res.sendJson` truyền 2 tham số, truyền array/primitive, hoặc không bọc `{ data }` / `{ data, pagination }`. **(khuôn base)**
- [chặn merge] Dùng `CustomError.CustomMessage(...)` (errorCode cứng 400); errorCode là số trần thay vì `ErrorCode.X`; message viết chuỗi trực tiếp thay vì hằng số trong `common/message.response.ts`. **(khuôn base)**
- [chặn merge] Controller tự trả lỗi thủ công (`res.status(400).json(...)`) thay vì `throw`/`next(error)` để error handler tập trung xử lý.
- [chặn merge] Error handler trả `error.stack` hoặc message lỗi hệ thống thô ra client ngoài môi trường development.

## Dữ liệu, event, job (BE §6–§8)
- [chặn merge] Schema Mongoose MỚI thiếu `timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }`; model Sequelize MỚI thiếu `underscored`/`timestamps`/`tableName`. **(khuôn base)**
- [chặn merge] Đổi schema Postgres mà PR không có migration (up + down) hoặc không cập nhật model trong cùng PR — CHỈ khi xác minh được danh sách file của PR; không xác minh được thì hỏi.
- [chặn merge] Tên event không theo `'event.<domain>.<pastTense>'` hoặc không là hằng số trong `<feature>.event.ts`; `EventBus.on` ngoài `*.event.ts`; event class MỚI không đăng ký trong `Application.registerEvents()` (xác minh trước khi báo); handler không tự `try/catch` + log; emit instance ORM thay vì DTO đã transform. **(khuôn base)**
- [chặn merge] Dùng EventBus cho việc cần retry/bền vững (phải dùng Bull/queue).
- [chặn merge] Job handler MỚI thiếu `try/catch`, thiếu `done()` hoặc `done(error)`; job mới không đăng ký trong `worker/router.ts` (xác minh trước khi báo); tên queue là chuỗi literal hoặc không kebab-case trong `config/jobs.ts`. **(khuôn base)**

## SHOULD
- [cảnh báo] Feature mới thiếu file theo khuôn (`type`, `biz`, `repo`, `mapper`, `event`); đặt tên `*.service.ts` thay vì `*.biz.ts`. **(khuôn base)**
- [cảnh báo] Tác vụ độc lập không chạy song song bằng `Promise.all`; việc nặng xử lý ngay trong request thay vì đẩy job.
- [cảnh báo] Query Mongo chỉ đọc không dùng `.lean()`; danh sách không dùng plugin `paginate`; thiếu index cho field hay truy vấn/unique.
- [cảnh báo] `express.json()`/`bodyParser` MỚI không đặt `limit`.
- [cảnh báo] Middleware MỚI không gọi `next()` ở mọi nhánh (treo request) — CHỈ khi toàn bộ thân middleware hiện trong diff.
- [nit] Middleware dùng chung chứa luật nghiệp vụ của một domain cụ thể.
