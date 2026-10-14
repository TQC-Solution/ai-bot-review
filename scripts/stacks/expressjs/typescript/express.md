# Quy tắc Express + TypeScript (bổ sung cho `expressjs/express.md`)
Nguồn: Coding Standards — Backend Express §3, §4 + CORE §3. CHỈ áp dụng cho file `.ts`.

- [cảnh báo] Ép `req.body`/`req.query`/`req.params` bằng `as any` hoặc `as any as T` thay vì khai báo kiểu request (generic `Request<Params, ResBody, ReqBody, Query>` hoặc interface riêng) sau khi đã validate.
- [cảnh báo] Mở rộng `Request` (ví dụ thêm `userId`) bằng `(req as any).userId` thay vì khai báo module augmentation (`declare global { namespace Express { interface Request { ... } } }`) hoặc kiểu dự án đã có.
- [nit] Schema Joi object không gắn generic theo interface (`Joi.object<IBody>()`), làm schema và kiểu lệch nhau.
- [nit] Interface/type request/response của endpoint mới đặt rải trong controller thay vì file type của domain (`*.type.ts` hoặc tương đương).
- [nit] Thiếu kiểu trả về tường minh cho hàm public của service/biz/repo MỚI.
