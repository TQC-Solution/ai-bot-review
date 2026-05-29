# Base Frontend - Architecture Rules

Tài liệu này mô tả cấu trúc và quy ước của dự án `base-frontend`.
Mục đích: giúp AI và Developer hiểu vị trí trách nhiệm của từng thành phần để review, maintain và refactor an toàn; giữ đúng pattern hiện có, không tạo rule quá chặt.

## 1. Tổng quan dự án

`base-frontend` là ứng dụng **Next.js 15 (App Router, Turbopack)** + **React 19** + **TypeScript (`strict: true`)**. Thư viện chính:
- **Ant Design 5** (`antd`, `@ant-design/nextjs-registry`, patch React 19) cho UI.
- **Redux Toolkit** + **react-redux** cho global state.
- **axios** cho HTTP, **NextAuth** cho xác thực, **react-google-recaptcha** cho captcha.
- **SCSS (sass)** + **Tailwind**, **next/font** cho typography.

Dùng **path alias** `@/*` → `src/*` (khai báo trong `tsconfig.json`). Khi review/sửa import nên dùng alias `@/...` thay vì đường dẫn tương đối dài.

## 2. Cấu trúc thư mục & trách nhiệm

### `src/app` — App Router (Presentation & Routing)
- `layout.tsx`: root layout — khai báo `metadata`/`viewport` (SEO), `next/font`, bọc `AntdRegistry` + `ConfigProvider` (theme antd).
- `page.tsx`: page entrypoint, compose các component.
- `globals.scss`: style toàn cục.
- `robots.ts`, `sitemap.ts`: cấu hình SEO theo chuẩn Next.js Metadata API.
- `_component/`: component riêng tư của route (private, không tái sử dụng ngoài route đó).
- `api/auth/[...nextauth]/route.ts`: Route Handler của NextAuth (`CredentialsProvider`, callbacks `jwt`/`session`, `secret` từ env server).

### `src/components` — UI dùng chung
Component tái sử dụng nhiều nơi (`Header/`, `Footer/`...), mỗi component một thư mục với `index.tsx`. Chỉ lo hiển thị, nhận dữ liệu qua props.

### `src/services` — Tầng gọi API (Data)
Hàm gọi API theo domain (ví dụ `auth.ts` với `loginPost`). Mỗi hàm dùng `axiosInstance`, khai báo interface request/response rõ ràng. **Mọi call API phải đi qua tầng này**, không gọi axios/fetch raw trong component.

### `src/axios` — HTTP client hạ tầng
- `interceptors.ts`: tạo `axiosInstance` (baseURL từ `env.API_ENDPOINT`, timeout, header chung), request/response interceptor, helper `clearAccessToken`. Response interceptor trả thẳng `response.data`. Xử lý token/401 tập trung ở đây.

### `src/redux` — Global state
- `store.ts`: `configureStore`, export type `RootState` và `AppDispatch`.
- `StoreProvider.tsx`: provider (`"use client"`) bọc app.
- `slice/`: định nghĩa slice (createSlice). `selector/`: selector tái sử dụng.

### `src/configs` — Cấu hình runtime
- `env.ts`: gom biến môi trường. CHỈ biến có tiền tố `NEXT_PUBLIC_` mới được expose ra client (`API_ENDPOINT`, `ORIGIN`, `RECAPCHA_SITE_KEY`). Đọc env qua object `env` này, không rải `process.env` khắp nơi.

### `src/hooks`, `src/utils` — Tái sử dụng
- `hooks/`: custom hook (logic UI tái sử dụng).
- `utils/`: hàm helper thuần, không side-effect khó kiểm soát.

### `src/styles` — Style
- `variables.scss`, `index.scss`: design token, biến SCSS dùng chung.

## 3. Quy tắc làm việc & dependency (Next.js App Router)

1. **Server vs Client Component:** mặc định là Server Component. CHỈ thêm `"use client"` khi cần state/effect/event handler/browser API (như `StoreProvider`). Không đánh dấu client thừa.
2. **Không lộ secret ra client:** secret server (ví dụ `NEXTAUTH_SECRET`) chỉ dùng trong code server (route handler, server component). Tuyệt đối không đọc biến không có `NEXT_PUBLIC_` trong Client Component.
3. **Gọi API qua tầng service:** UI/component không gọi `axios`/`fetch` raw. Dùng hàm trong `src/services` (đi qua `axiosInstance` để thống nhất baseURL, header, xử lý lỗi/401).
4. **Cấu hình tập trung:** lấy config qua `@/configs/env`; không hard-code endpoint, site key, origin trong component.
5. **Global state tối giản:** chỉ đưa vào Redux state thực sự dùng chung nhiều nơi; state cục bộ để tại component/feature. Dùng type `RootState`/`AppDispatch` khi truy cập store.
6. **UI dùng Ant Design:** ưu tiên component `antd` + theme qua `ConfigProvider` thay vì tự dựng lại; giữ nhất quán với layout hiện có.
7. **Tối ưu Next.js:** dùng `next/image` (`<Image>`) thay `<img>`, `next/link` (`<Link>`) cho điều hướng nội bộ, `next/font` cho font. Có `alt`/kích thước cho ảnh.
8. **SEO:** trang quan trọng khai báo `metadata`; giữ `robots.ts`/`sitemap.ts` đồng bộ khi thêm route public.
9. **TypeScript strict:** khai báo kiểu Props tường minh, tránh `any`/`as any` (hiện còn vài chỗ ép kiểu trong NextAuth callbacks/service — không nhân rộng thêm). Định nghĩa interface cho request/response API.
10. **Side-effect có kiểm soát:** API call, redirect, localStorage, analytics đặt trong hook/service/interceptor, không rải rác trong thân render component.

## 4. Quy ước đặt tên & tổ chức

- Component dùng chung: thư mục PascalCase + `index.tsx` (`components/Header/index.tsx`).
- Component riêng của route: đặt trong `app/.../_component`.
- Hàm service đặt theo hành động + domain (`loginPost`), kèm interface `XxxRequest` / `XxxResponse`.
- Import nội bộ dùng alias `@/...`.
- Style dùng SCSS module/biến trong `src/styles`; ưu tiên token thay vì hardcode màu/spacing.

## 5. Nguyên tắc refactor cho AI

- Bảo toàn hợp đồng UI/route: không đổi props shape, return contract hay route params nếu chưa có yêu cầu.
- Không phá vỡ luồng auth (NextAuth) và interceptor axios khi refactor.
- Không thêm dependency mới nếu antd/redux-toolkit/axios hiện có đã đáp ứng.
- Giữ ranh giới tầng: Presentation (`app`/`components`) → Service (`services`/`axios`) → State (`redux`) → Config (`configs`).
- Ưu tiên thay đổi nhỏ, không đổi hành vi loading/error/empty state trừ khi được yêu cầu.
