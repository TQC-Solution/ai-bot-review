# Quy tắc TypeScript — dự án TS chạy `strict: true`
Nguồn: Coding Standards CORE §3. CHỈ áp dụng cho dòng `+` trong file `.ts`/`.tsx`.
(File này có bản giống hệt trong các stack TypeScript khác; sửa một chỗ thì đồng bộ các chỗ còn lại.)

## Kiểu dữ liệu
- [cảnh báo] Thêm `any` mới (`: any`, `as any`, `any[]`, `Promise<any>`) mà không có comment `// eslint-disable-next-line @typescript-eslint/no-explicit-any -- <lý do>`. Gợi ý interface cụ thể hoặc `unknown` + type guard. [📐 Core §3; Core §10.3]
- [cảnh báo] Ép kiểu hai lần `as unknown as T` / `as any as T`. [📐 Core §3]
- [cảnh báo] Thêm `@ts-ignore` / `@ts-nocheck`, `eslint-disable` cho cả file, hoặc disable từng dòng không ghi `-- <lý do>`. [📐 Core §3; Core §10.3]
- [cảnh báo] Diff nới `tsconfig` (tắt `strict`, `noImplicitAny`, `strictNullChecks`...). [📐 Core §3; Core §10.3]
- [cảnh báo] Non-null assertion `!` trên giá trị mà CHÍNH diff cho thấy có thể null/undefined (kết quả `find(...)`, `findOne(...)`, `Map.get(...)`, tham số optional `?:`). KHÔNG báo khi không nhìn thấy nguồn gốc của giá trị. [📐 Core §3]
- [cảnh báo] Truy cập thuộc tính trên giá trị mà CHÍNH diff cho thấy có thể null/undefined (ví dụ `const user = await repo.findOne(...)` rồi dùng `user.id` ngay). KHÔNG suy đoán khi không thấy khai báo/kiểu. [📐 Core §3]
- [nit] `switch` trên union/enum mà diff hiện đầy đủ cả kiểu lẫn các nhánh, nhưng thiếu nhánh và không có kiểm tra `never` ở `default`. [📐 Core §3]
- [nit] Dùng `||` để đặt mặc định cho giá trị có thể hợp lệ là `0`/`""`/`false` (nên dùng `??`). [📐 Core §3]
- [nit] Thêm `enum` mới thay vì union string literal, trừ enum dự án đã chốt (ví dụ `ErrorCode`). [📐 Core §3]

## Import
- [cảnh báo] Import tương đối dài (`../../../`) trong khi dự án có path alias tương ứng; dùng alias không khai báo trong `tsconfig.json`. [📐 Core §3]
- [nit] Import chỉ dùng làm kiểu nhưng không dùng `import type`. [📐 Core §3]
- [nit] File `.js` mới trong thư mục mã nguồn của dự án TypeScript (ngoại lệ: migration, config tool). [📐 Core §3]
