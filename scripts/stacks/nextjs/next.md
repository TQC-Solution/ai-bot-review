# Quy tắc Next.js — bổ sung cho `nextjs/react.md`
Nguồn: Coding Standards — Frontend React/Next.js v1.0 §5, §8. Áp dụng cho App Router; với Pages Router, chỉ áp dụng các mục không nói về Server/Client Component.

## Server vs Client Component (FE §5)
- [chặn merge] Client Component (`"use client"`) đọc biến môi trường không có tiền tố `NEXT_PUBLIC_`, hoặc import module server-only (DB client, secret, `next/headers`, file đọc `process.env` bí mật).
- [chặn merge] Secret đặt trong biến `NEXT_PUBLIC_*` (sẽ bị đóng gói ra trình duyệt).
- [cảnh báo] Thêm `"use client"` cho page/layout trong khi chỉ một phần nhỏ cần tương tác — nên đẩy xuống component lá. Không báo khi file dùng hook/state/event handler/browser API.
- [cảnh báo] Dùng `window`/`document`/`localStorage` trong Server Component hoặc ngoài `useEffect` của Client Component (lỗi khi render phía server).
- [cảnh báo] Import Server Component vào Client Component (phải truyền qua `children`/props).
- [cảnh báo] Fetch dữ liệu ở client bằng `useEffect` cho dữ liệu có thể lấy ở Server Component, khi trang đó là trang public cần SEO — dạng câu hỏi.

## Route handler & server action
- [chặn merge] Route handler/server action MỚI thao tác dữ liệu người dùng mà không kiểm tra session/quyền phía server (chỉ dựa vào UI).
- [cảnh báo] Route handler/server action MỚI không validate input.
- [cảnh báo] Lấy session không qua API của thư viện auth dự án dùng (ví dụ `getServerSession`/`auth()` của NextAuth).

## Tối ưu & SEO (FE §5)
- [cảnh báo] `<img>` thay vì `next/image`; `<a>` cho điều hướng nội bộ thay vì `next/link` — trừ ảnh/link ngoài có lý do rõ.
- [cảnh báo] Domain/URL hardcode trong `metadata`, `robots.ts`, `sitemap.ts` thay vì cấu hình env (ví dụ `env.ORIGIN`).
- [nit] Page public MỚI thiếu `metadata`/`generateMetadata`; route public mới không cập nhật `sitemap.ts`.
- [nit] Font nạp bằng thẻ `<link>` thay vì `next/font`; component nặng chỉ dùng phía client không dùng `next/dynamic`.

## Cấu hình
- [cảnh báo] Đọc `process.env` ngoài module cấu hình env của dự án (ví dụ `configs/env.ts`), trừ `next.config.*`.
