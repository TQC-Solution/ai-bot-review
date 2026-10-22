# Base Frontend — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của dự án `base-frontend` (và các dự án fork từ nó). Căn cứ: 📐 Coding Standards — Frontend React/Next.js v1.0.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.

## 1. Tổng quan
- **Next.js 15 (App Router, Turbopack)** + **React 19** + **TypeScript `strict: true`**.
- UI: **Ant Design 5** (`@ant-design/nextjs-registry`, theme qua `ConfigProvider`), **SCSS** + **Tailwind**, `next/font`.
- State: **Redux Toolkit** + react-redux. HTTP: **axios** qua `axiosInstance`. Auth: **NextAuth** (`CredentialsProvider`). Captcha: `react-google-recaptcha`.
- Path alias `@/*` → `src/*`.

## 2. Cấu trúc thư mục & trách nhiệm
- `src/app/`: App Router. `layout.tsx` (metadata/viewport, `next/font`, `AntdRegistry` + `ConfigProvider`), `page.tsx`, `globals.scss`, `robots.ts`, `sitemap.ts`, `_component/` (component riêng của route), `api/auth/[...nextauth]/route.ts` (NextAuth, `secret` từ env server).
- `src/components/<Name>/index.tsx`: component dùng chung, chỉ hiển thị, nhận dữ liệu qua props.
- `src/services/<domain>.ts`: hàm gọi API (ví dụ `loginPost`) dùng `axiosInstance`, có interface `XxxRequest`/`XxxResponse`.
- `src/axios/interceptors.ts`: tạo `axiosInstance` (baseURL từ `env.API_ENDPOINT`, timeout, header), interceptor request/response; response interceptor trả thẳng `response.data`; xử lý token/401 tập trung; `clearAccessToken`.
- `src/redux/`: `store.ts` (`RootState`, `AppDispatch`), `StoreProvider.tsx` (`"use client"`), `slice/`, `selector/`.
- `src/configs/env.ts`: gom biến môi trường; chỉ biến `NEXT_PUBLIC_*` (`API_ENDPOINT`, `ORIGIN`, `RECAPCHA_SITE_KEY`) ra client.
- `src/hooks/`, `src/utils/`, `src/styles/` (`variables.scss`, `index.scss`).

## 3. Luật review

### 3.1. Ranh giới tầng — `app/components → services/axios → redux → configs`
- [chặn merge] Client Component đọc biến môi trường không có `NEXT_PUBLIC_` (ví dụ `NEXTAUTH_SECRET`) hoặc import module server-only. [📐 FE §5.1]
- [cảnh báo] Component/hook gọi `axios`/`fetch` trực tiếp thay vì hàm trong `src/services` dùng `axiosInstance`; tạo `axios.create` mới ngoài `src/axios/interceptors.ts`. [📐 FE §7]
- [cảnh báo] Xử lý 401/token rải rác trong component/service thay vì interceptor. [📐 FE §7]
- [cảnh báo] Đọc `process.env` ngoài `src/configs/env.ts` (trừ `next.config.*` và route NextAuth phía server). [📐 FE §7]
- [cảnh báo] Hardcode endpoint, origin, site key trong component. [📐 FE §7]

### 3.2. Service & API
- [cảnh báo] Hàm service mới thiếu interface request/response; đường dẫn API mới không theo `/v2`. [📐 FE §7]
- [cảnh báo] Xử lý lỗi dựa vào `message` thay vì `error_code` của envelope. [📐 FE §7; Core §4.2]
- [nit] Tên hàm service không theo mẫu hành động + domain (`loginPost`, `userListGet`). [Dự án]

### 3.3. Component, Next.js, UI
- [cảnh báo] `"use client"` cho page/layout khi chỉ một phần cần tương tác. [📐 FE §5.1]
- [cảnh báo] `<img>` thay vì `next/image`; `<a>` nội bộ thay vì `next/link`. [📐 FE §5.3]
- [cảnh báo] Style tĩnh bằng `style={{...}}`; hardcode màu/spacing thay vì biến trong `src/styles` hoặc token AntD. [📐 FE §3]
- [cảnh báo] Tự dựng lại form/table/modal khi AntD đã có. [📐 FE §3]
- [cảnh báo] `React.FC`/`defaultProps`; props không khai báo bằng `interface`. [📐 FE §2.1]
- [nit] Page public mới thiếu `metadata`; route public mới không cập nhật `sitemap.ts`. [📐 FE §5.3]

### 3.4. State
- [cảnh báo] Slice mới không đặt trong `redux/slice/`; đọc `state.x` trực tiếp lặp lại thay vì selector trong `redux/selector/`. [📐 FE §6]
- [cảnh báo] Đưa state chỉ dùng trong một màn hình vào store. [📐 FE §6]

### 3.5. Auth
- [chặn merge] Callback NextAuth trả/log mật khẩu hoặc token thô. [📐 FE §5.2; Core §7]
- [cảnh báo] Lấy session không qua API NextAuth (`getServerSession`, `useSession`); chỉ ẩn UI để phân quyền. [📐 FE §5.2; FE §8]

### Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.
- [cảnh báo] Test service trong `src/services` không mock `axiosInstance` (`vi.mock('@/axios/interceptors')`) hoặc gọi API thật. [📐 Test FE §3.2]

## 4. Quy ước đặt tên & tổ chức
- [nit] Component dùng chung: thư mục PascalCase + `index.tsx`; component riêng route đặt trong `app/.../_component`. [📐 FE §1; Core §2]
- [nit] Import nội bộ dùng alias `@/...` thay vì đường dẫn tương đối dài. [📐 FE §1]

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- NextAuth callbacks và một số service hiện còn `as any`. Chỉ báo khi code MỚI thêm `as any`.
- (Bổ sung tại đây các mẫu báo sai lặp lại mà dev đã xác nhận.)

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Giữ props shape, route params, hành vi loading/error/empty state nếu không được yêu cầu đổi.
- Không phá luồng NextAuth và interceptor axios.
- Không thêm dependency mới nếu AntD/RTK/axios đã đáp ứng. Ưu tiên thay đổi nhỏ, đúng tầng.
