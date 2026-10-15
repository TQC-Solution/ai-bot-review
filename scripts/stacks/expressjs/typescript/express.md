# Quy tắc Express + TypeScript (bổ sung cho `expressjs/express.md`)
Nguồn: Coding Standards — Backend Express §3, §4, §11, §12 + CORE §3 + checklist AI review `REVIEW.express.md`. CHỈ áp dụng cho file `.ts` (trừ mục Build).

- [chặn merge] File JS thuần MỚI ngoài `src/migrations/`; script build bỏ bước `tscpaths` (`rimraf dist → tsc → tscpaths`). (BE §12.4)
- [cảnh báo] Ép `req.body`/`req.query`/`req.params` bằng `as any` hoặc `as any as T` thay vì khai báo kiểu request (generic `Request<Params, ResBody, ReqBody, Query>` hoặc interface riêng) sau khi đã validate.
- [cảnh báo] Mở rộng `Request` (ví dụ thêm `userId`) bằng `(req as any).userId` thay vì khai báo module augmentation (`declare global { namespace Express { interface Request { ... } } }`) hoặc kiểu dự án đã có.
- [cảnh báo] Schema Joi object không gắn generic theo interface (`Joi.object<IBody>()`), làm schema và kiểu lệch nhau.
- [cảnh báo] Interface MỚI không tiền tố `I`, enum MỚI không tiền tố `E`; `export default` ngoài router feature, logger, model Mongoose. **(khuôn base)**
- [nit] Interface/type request/response của endpoint mới đặt rải trong controller thay vì file type của domain (`*.type.ts` hoặc tương đương).
- [nit] Thiếu kiểu trả về tường minh cho hàm public của service/biz/repo MỚI.
