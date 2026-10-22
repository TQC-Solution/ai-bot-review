# Quy tắc Next.js — bổ sung cho `nextjs/react.md`
Nguồn: Coding Standards — Frontend React/Next.js v1.0 §5, §8. Áp dụng cho App Router; với Pages Router, chỉ áp dụng các mục không nói về Server/Client Component.

## Server vs Client Component
- [chặn merge] Client Component (`"use client"`) đọc biến môi trường không có tiền tố `NEXT_PUBLIC_`, hoặc import module server-only (DB client, secret, `next/headers`, file đọc `process.env` bí mật). [📐 FE §5.1]
- [chặn merge] Secret đặt trong biến `NEXT_PUBLIC_*` (sẽ bị đóng gói ra trình duyệt). [📐 FE §5.1; Core §5]
- [cảnh báo] Thêm `"use client"` cho page/layout trong khi chỉ một phần nhỏ cần tương tác — nên đẩy xuống component lá. Không báo khi file dùng hook/state/event handler/browser API. [📐 FE §5.1]
- [cảnh báo] Dùng `window`/`document`/`localStorage` trong Server Component hoặc ngoài `useEffect` của Client Component (lỗi khi render phía server). [📐 FE §5.1]
- [cảnh báo] Import Server Component vào Client Component (phải truyền qua `children`/props). [📐 FE §5.1]
- [cảnh báo] Fetch dữ liệu ở client bằng `useEffect` cho dữ liệu có thể lấy ở Server Component, khi trang đó là trang public cần SEO — dạng câu hỏi. [📐 FE §5.1; FE §4]

## Route handler & server action
- [chặn merge] Route handler/server action MỚI thao tác dữ liệu người dùng mà không kiểm tra session/quyền phía server (chỉ dựa vào UI). [📐 FE §5.2; FE §8]
- [cảnh báo] Route handler/server action MỚI không validate input. [📐 Core §5]
- [cảnh báo] Lấy session không qua API của thư viện auth dự án dùng (ví dụ `getServerSession`/`auth()` của NextAuth). [📐 FE §5.2]

## Tối ưu & SEO
- [cảnh báo] `<img>` thay vì `next/image`; `<a>` cho điều hướng nội bộ thay vì `next/link` — trừ ảnh/link ngoài có lý do rõ. [📐 FE §5.3]
- [cảnh báo] Domain/URL hardcode trong `metadata`, `robots.ts`, `sitemap.ts` thay vì cấu hình env (ví dụ `env.ORIGIN`). [📐 FE §5.3]
- [nit] Page public MỚI thiếu `metadata`/`generateMetadata`; route public mới không cập nhật `sitemap.ts`. [📐 FE §5.3]
- [nit] Font nạp bằng thẻ `<link>` thay vì `next/font`; component nặng chỉ dùng phía client không dùng `next/dynamic`. [📐 FE §5.3; FE §4]

## Cấu hình
- [cảnh báo] Đọc `process.env` ngoài module cấu hình env của dự án (ví dụ `configs/env.ts`), trừ `next.config.*`. [📐 FE §7]
