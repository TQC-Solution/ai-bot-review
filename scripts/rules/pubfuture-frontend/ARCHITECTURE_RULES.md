# PubFuture Frontend Architecture Diagram

Tài liệu này mô tả cấu trúc thư mục và chức năng của các module trong dự án PubFuture Frontend (TypeScript + React).
Mục đích: Hỗ trợ AI và Developer hiểu rõ vị trí trách nhiệm của từng thành phần để review, maintain và refactor an toàn.

## Cấu trúc tổng quan

Dự án được tổ chức theo hướng tách bạch giữa tầng giao diện, tầng nghiệp vụ và tầng hạ tầng tích hợp.

### 1. App Shell & Routing
Các thư mục này điều phối layout, điều hướng và lifecycle của ứng dụng.
* `/src/app` hoặc `/src/pages`: Định nghĩa route, page entrypoint và layout-level composition.
* `/src/layouts`: Chứa shared layout (MainLayout, AuthLayout, DashboardLayout).
* `/src/router`: Cấu hình route tree, guards, lazy loading.

### 2. Feature Modules
Các thư mục này chứa nghiệp vụ chính của từng miền chức năng, mỗi feature tự quản state và UI riêng.
* `/src/features`: Chia theo domain (ví dụ: `auth`, `profile`, `campaign`, `report`).
* `/src/components`: UI components dùng chung nhiều feature (button, modal, table, form control).
* `/src/hooks`: Custom hooks tái sử dụng, ưu tiên không chứa side-effect khó kiểm soát.
* `/src/store` hoặc `/src/state`: Quản lý global state (Redux, Zustand, Context), chỉ lưu trạng thái thực sự dùng toàn app.

### 3. Data & Infrastructure
Các thư mục này xử lý giao tiếp API và các tích hợp ngoài.
* `/src/services`: API client, request wrapper, authentication token handling.
* `/src/apis`: Định nghĩa endpoint theo từng domain, mapping request/response DTO.
* `/src/lib`: Các module hạ tầng (HTTP client instance, logger, analytics adapter, error tracker).
* `/src/utils` và `/src/constants`: Helper functions và hằng số dùng chung toàn dự án.

### 4. Assets & Configuration
* `/src/assets`: Images, icons, fonts, static files cho UI.
* `/src/styles`: Theme tokens, global styles, design-system variables.
* `/src/config`: Biến môi trường, runtime config, feature flags.


# PubFuture Frontend - Architectural Guidelines & Context cho AI

PubFuture Frontend được xây dựng theo hướng scalable frontend architecture. Hãy đọc kỹ các quy tắc dưới đây trước khi review hoặc đề xuất thay đổi code.

## 1. Phân tầng Kiến trúc (Layered Frontend)

Hệ thống được chia thành 3 tầng chính:
1. **Presentation Layer:** Route, page, component hiển thị dữ liệu và nhận user interaction.
2. **Domain/Feature Layer:** Hook nghiệp vụ, state orchestration, rules xử lý theo domain.
3. **Infrastructure Layer:** API client, external SDK, analytics, logging, persistence.

## 2. Ranh giới Module & Quy tắc phụ thuộc (Dependency Rules)

### A. Presentation Layer (UI)
Các file thuộc `app/pages/layouts/components` chỉ nên xử lý hiển thị và orchestration nhẹ.
* Không chứa business logic dài hoặc xử lý data phức tạp trực tiếp trong component.
* Không gọi API trực tiếp trong UI component nếu đã có `services/apis/hooks` trung gian.
* Ưu tiên truyền dữ liệu qua props/hook, tránh phụ thuộc chéo giữa các feature không liên quan.

### B. Feature/Domain Layer (Business)
Các file trong `features/hooks/store` là nơi đặt logic nghiệp vụ.
* Được phép điều phối state, validate dữ liệu, transform model trước khi render.
* Không import trực tiếp từ feature khác nếu không có contract rõ ràng (shared types/service).
* Khi cần dùng chung logic giữa nhiều feature, trích xuất sang `hooks` hoặc `lib` thay vì copy.

### C. Infrastructure Layer (Data + External)
Các file trong `services/apis/lib/config` chịu trách nhiệm giao tiếp bên ngoài.
* Tất cả API call phải đi qua lớp này để thống nhất auth, retry, timeout, error mapping.
* Không để component gọi fetch/axios raw trực tiếp nếu project đã có HTTP wrapper.
* Secret/config nhạy cảm chỉ đọc từ environment config, không hardcode trong codebase.

## 3. Quy tắc Refactoring cho AI
1. **Bảo toàn hợp đồng UI/Feature:** Khi refactor component hoặc hook public, không đổi props shape, return contract hoặc route params nếu chưa có yêu cầu rõ ràng.
2. **Single Responsibility:** Mỗi component/hook/service chỉ nên có một trách nhiệm chính, tách nhỏ khi vượt ngưỡng khó đọc.
3. **State tối giản:** Chỉ đưa vào global store những state dùng xuyên nhiều page; state cục bộ nên để tại feature/component.
4. **An toàn side-effect:** Side-effect (API call, analytics, local storage, redirect) phải được đặt trong hook/service có kiểm soát lifecycle.
5. **Không phá vỡ trải nghiệm:** Mọi refactor liên quan loading, error state, empty state phải giữ nguyên hành vi UX hiện tại trừ khi có yêu cầu thay đổi.
