# PubFuture Frontend — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của PubFuture Frontend (TypeScript + React). Căn cứ: 📐 Coding Standards — Frontend React/Next.js v1.0.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.
Lưu ý: cấu trúc dưới đây là khung tổng quát; tên thư mục có thể khác trong repo. Khi review, theo pattern của feature gần nhất; không báo lỗi chỉ vì tên thư mục khác mô tả.

## 1. Tổng quan
Ba tầng: **Presentation** (route, page, component) → **Feature/Domain** (hook nghiệp vụ, state, rule theo domain) → **Infrastructure** (API client, SDK ngoài, analytics, logging, persistence).

## 2. Cấu trúc thư mục & trách nhiệm
- App shell: `src/app` hoặc `src/pages` (route, page), `src/layouts` (MainLayout, AuthLayout, DashboardLayout), `src/router` (route tree, guard, lazy loading).
- Feature: `src/features/<domain>` (tự quản UI + state riêng), `src/components` (UI dùng chung), `src/hooks` (hook tái sử dụng), `src/store`/`src/state` (state toàn app).
- Data: `src/services` (API client, wrapper, token), `src/apis` (endpoint theo domain, DTO), `src/lib` (HTTP client instance, logger, analytics, error tracker), `src/utils`, `src/constants`.
- `src/assets`, `src/styles` (theme token, global style), `src/config` (env, runtime config, feature flag).

## 3. Luật review

### 3.1. Ranh giới tầng
- [cảnh báo] Component/page gọi `fetch`/`axios` raw khi dự án đã có HTTP wrapper trong `services`/`apis`/`lib`. [📐 FE §7]
- [cảnh báo] Feature import trực tiếp nội bộ của feature khác (component/hook/state riêng) thay vì qua shared type/service/hook dùng chung. [📐 FE §1]
- [cảnh báo] Business logic dài/transform dữ liệu phức tạp trong thân component thay vì hook/feature. [📐 FE §2.1]
- [cảnh báo] Side-effect (API call, analytics, localStorage, redirect) rải trong thân render thay vì hook/service có kiểm soát lifecycle. [📐 FE §4]
- [nit] Copy logic giữa feature thay vì tách vào `hooks`/`lib` — CHỈ khi diff hiện cả hai đoạn trùng. [📐 Core §1.2]

### 3.2. API, config, bảo mật
- [chặn merge] Secret/token hardcode trong code client. [📐 FE §8; Core §5]
- [cảnh báo] Endpoint/URL hardcode thay vì `src/config`; đọc env rải rác. [📐 FE §7]
- [cảnh báo] DTO request/response mới không có kiểu; xử lý lỗi dựa vào `message` thay vì `error_code`. [📐 FE §7; Core §4.2]

### 3.3. State & UX
- [cảnh báo] Đưa state chỉ dùng trong một page/feature vào store toàn cục. [📐 FE §6]
- [cảnh báo] Thay đổi làm mất loading/error/empty state đang có của màn hình mà PR không nêu. [Dự án]
- [cảnh báo] Đổi props shape, return contract của component/hook dùng chung hoặc route params mà PR không nêu. [Dự án]

### Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.

## 4. Quy ước đặt tên
- [nit] Component PascalCase; hook `useXxx`; file/thư mục theo pattern feature gần nhất. [📐 FE §1; Core §2]

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- (Bổ sung tại đây các chỗ code cũ chưa theo chuẩn và các mẫu báo sai lặp lại mà dev đã xác nhận.)

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Bảo toàn contract UI/feature; giữ hành vi UX; mỗi component/hook/service một trách nhiệm chính; ưu tiên thay đổi nhỏ.
