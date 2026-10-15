# Quy tắc TypeScript — dự án TS chạy `strict: true`
Nguồn: Coding Standards CORE §3 + checklist AI review `REVIEW.<stack>.md` (mục "TypeScript chung"). CHỈ áp dụng cho dòng `+` trong file `.ts`/`.tsx`.
(File này có bản giống hệt trong các stack TypeScript khác; sửa một chỗ thì đồng bộ các chỗ còn lại.)

## Kiểu dữ liệu & cấu hình
- [chặn merge] Thêm `any` mới (`: any`, `as any`, `any[]`, `Promise<any>`) mà không có comment `// eslint-disable-next-line @typescript-eslint/no-explicit-any -- <lý do>`. Gợi ý interface cụ thể hoặc `unknown` + type guard.
- [chặn merge] Ép kiểu hai lần `as unknown as T` / `as any as T`; thêm `@ts-ignore` / `@ts-nocheck`.
- [chặn merge] Diff tắt `strict` hoặc nới `tsconfig` (`noImplicitAny`, `strictNullChecks`, `skipLibCheck` mới bật để che lỗi...).
- [chặn merge] `eslint-disable` cho cả file, hoặc disable từng dòng không ghi `-- <lý do>`.
- [cảnh báo] Non-null assertion `!` trên giá trị mà CHÍNH diff cho thấy có thể null/undefined (kết quả `find(...)`, `findOne(...)`, `Map.get(...)`, tham số optional `?:`). KHÔNG báo khi không nhìn thấy nguồn gốc của giá trị.
- [cảnh báo] Truy cập thuộc tính trên giá trị mà CHÍNH diff cho thấy có thể null/undefined (ví dụ `const user = await repo.findOne(...)` rồi dùng `user.id` ngay). KHÔNG suy đoán khi không thấy khai báo/kiểu.
- [cảnh báo] Dùng `||` để đặt mặc định cho giá trị có thể hợp lệ là `0`/`""`/`false` (nên dùng `??`). KHÔNG báo khi chuỗi rỗng/0 rõ ràng cũng cần thay bằng mặc định.
- [cảnh báo] Thêm `enum` mới thay vì union string literal, trừ enum dự án đã chốt (ví dụ `ErrorCode`).
- [cảnh báo] Ép kiểu `as` tuỳ tiện để bỏ qua kiểm tra kiểu khi có thể thu hẹp bằng type guard hoặc khai báo kiểu đúng.
- [nit] `switch` trên union/enum mà diff hiện đầy đủ cả kiểu lẫn các nhánh, nhưng thiếu nhánh và không có kiểm tra `never` ở `default`.

## Import & export
- [chặn merge] Import tương đối dài (`../../../`) trong khi dự án có path alias tương ứng; dùng alias không khai báo trong `tsconfig.json`.
- [cảnh báo] Import chỉ dùng làm kiểu nhưng không dùng `import type`.
- [cảnh báo] Dùng `export default` khi framework không bắt buộc (ưu tiên named export) — trừ các ngoại lệ dự án đã chốt (xem luật stack/dự án).
- [nit] File `.js` mới trong thư mục mã nguồn của dự án TypeScript (ngoại lệ: migration, config tool).
