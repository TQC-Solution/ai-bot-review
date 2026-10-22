# PubStar Web — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của `pubstar-web`. Căn cứ: 📐 Coding Standards — Frontend React/Next.js v1.0, áp dụng mức "nhẹ": theo pattern có sẵn của màn hình gần nhất, không ép refactor code cũ.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.
Dự án này ưu tiên ít nhiễu: các mục FE chung không có trong luật dưới đây (ví dụ Redux, `/v2`, `configs/env.ts`) KHÔNG áp dụng nếu repo không dùng.

## 1. Tổng quan
Next.js 14 (App Router), React 18, TypeScript, Ant Design, SCSS, API client sinh từ OpenAPI, đa ngôn ngữ theo `[locale]`.

## 2. Cấu trúc thư mục & trách nhiệm
- `src/app/[locale]/(auth)`: đăng nhập, đăng ký, quên mật khẩu, xác thực email.
- `src/app/[locale]/(home)`: trang public (landing, privacy, terms).
- `src/app/[locale]/(protected)`: màn hình cần đăng nhập (user dashboard, admin).
- `src/components`: form, modal, table, layout, icon, auth component dùng lại.
- `src/hooks`: fetch option, notification, filter, view-as-publisher...
- `src/services/openapi`: client sinh từ `swagger.json` — KHÔNG sửa tay.
- `src/utils`: helper, constant, interface. `src/navigation`, `src/i18n.ts`: điều hướng, i18n. `public/assets`: static assets.

## 3. Luật review

### 3.1. Auth & quyền
- [chặn merge] Màn hình/route mới cần đăng nhập đặt ngoài `(protected)` hoặc bỏ qua protected layout/kiểm tra quyền hiện có. [📐 FE §5.2; FE §8]
- [chặn merge] Diff gỡ bỏ logic quyền, role, view-as-publisher hiện có mà không có thay thế. [📐 FE §8]
- [cảnh báo] Chức năng admin mới chỉ ẩn nút theo role mà không theo pattern kiểm quyền của màn hình admin khác — dạng câu hỏi. [📐 FE §8]

### 3.2. API
- [cảnh báo] Sửa tay file trong `src/services/openapi` (phải sửa `swagger.json` rồi generate lại). KHÔNG review nội dung code sinh tự động. [Dự án]
- [cảnh báo] Gọi `fetch`/`axios` trực tiếp cho endpoint đã có trong `DefaultApi`; tự khai báo lại type đã có trong client OpenAPI. [📐 FE §7]
- [cảnh báo] Hardcode URL API/secret trong component. [📐 FE §5.1; Core §5]

### 3.3. Next.js & UI
- [cảnh báo] Thêm `"use client"` cho page/layout không dùng hook/state/event/browser API. [📐 FE §5.1]
- [cảnh báo] Text hiển thị mới hardcode trong màn hình ĐANG dùng translation — KHÔNG áp dụng cho màn hình chưa dùng i18n, KHÔNG yêu cầu refactor text cũ. [Dự án]
- [cảnh báo] Điều hướng nội bộ không dùng helper trong `src/navigation` (mất locale) — khi màn hình đó đang dùng. [Dự án]
- [nit] Tự dựng lại form/table/modal khi `src/components` hoặc AntD đã có; màn hình CRUD/list mới lệch UX so với màn hình cùng loại. [📐 Core §1.2]
- [nit] SCSS đặt xa component đang dùng thay vì cạnh màn hình theo pattern hiện tại. [📐 FE §3]

### 3.4. TypeScript
- [cảnh báo] `any` mới cho dữ liệu API quan trọng khi type OpenAPI đã có. [📐 Core §3; FE §11.3]
- KHÔNG báo việc thiếu generic/phân tầng cho feature nhỏ.

### Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.
- KHÔNG viết/yêu cầu test cho `src/services/openapi` (code sinh tự động); test mock `DefaultApi`.

## 4. Quy ước đặt tên
- [nit] Theo pattern file/thư mục của màn hình gần nhất. [Dự án]

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- Các `eslint-disable` và comment hiện có: không đề xuất xoá.
- Text cũ chưa i18n, màn hình cũ chưa theo chuẩn FE mới: chỉ báo khi code MỚI.

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Bảo toàn route, URL, query param, behavior public. Không đổi cách dùng API khi chưa kiểm tra OpenAPI type.
- Thay đổi lớn ảnh hưởng nhiều route, API client, auth, permission: đọc file liên quan và xác nhận phạm vi trước. Ưu tiên thay đổi nhỏ.
