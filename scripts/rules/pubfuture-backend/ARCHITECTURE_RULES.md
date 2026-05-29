# PubFuture Backend Architecture Diagram

Tài liệu này mô tả cấu trúc thư mục và chức năng của các module trong dự án PubFuture Backend (Node.js + ExpressJS).
Mục đích: Hỗ trợ AI và Developer hiểu rõ ranh giới trách nhiệm của từng thành phần để review, maintain và refactor an toàn.

## Cấu trúc tổng quan

Dự án được tổ chức theo hướng tách bạch giữa tầng HTTP, tầng nghiệp vụ và tầng truy cập dữ liệu/hạ tầng.

### 1. App Bootstrap & Runtime
Những thư mục/file này phụ trách khởi tạo server, middleware và lifecycle của ứng dụng.
* `/src/app` hoặc `/src/server`: Khởi tạo Express app, đăng ký middleware, global error handler.
* `/src/config`: Quản lý biến môi trường, runtime config, feature flags, app constants.
* `/src/bootstrap`: Khởi tạo dependency, kết nối DB/queue/cache, startup jobs.

### 2. HTTP Interface Layer
Tầng này tiếp nhận request và chuyển giao vào nghiệp vụ.
* `/src/routes`: Định nghĩa endpoint, route grouping theo domain và API versioning.
* `/src/controllers`: Parse request, gọi service, map response status/body.
* `/src/middlewares`: Auth, validation, logging, rate limit, request context.
* `/src/validators`: Validate schema đầu vào (Joi, Zod, Yup...), không đặt business logic phức tạp.

### 3. Domain & Application Layer
Tầng này chứa logic nghiệp vụ chính của hệ thống.
* `/src/modules` hoặc `/src/features`: Chia theo domain (ví dụ: `auth`, `user`, `campaign`, `report`).
* `/src/services`: Xử lý use-case, orchestration giữa nhiều repository/integration.
* `/src/use-cases`: Đóng gói nghiệp vụ theo từng hành động rõ ràng.
* `/src/domain`: Entity, value object, domain rules và domain error.

### 4. Data & Infrastructure Layer
Tầng này giao tiếp với hệ thống bên ngoài và persistence.
* `/src/repositories`: Truy vấn DB qua ORM/query builder, map data model <-> domain model.
* `/src/models`: Định nghĩa schema ORM, migration metadata, DB DTO.
* `/src/integrations` hoặc `/src/clients`: Gọi API bên thứ 3 (payment, email, analytics, storage...).
* `/src/lib` và `/src/utils`: Helper chia sẻ, logger, telemetry adapter, wrappers dùng chung.

### 5. Test & Operational Support
* `/tests` hoặc `/src/__tests__`: Unit test, integration test, route test.
* `/scripts`: Script phục vụ migration, seed, maintenance task.
* `/docs`: API contract, runbook, operational guideline.


# PubFuture Backend - Architectural Guidelines & Context cho AI

PubFuture Backend được xây dựng theo hướng scalable backend architecture với ExpressJS. Hãy đọc kỹ các quy tắc dưới đây trước khi review hoặc đề xuất thay đổi code.

## 1. Phân tầng Kiến trúc (Layered Backend)

Hệ thống được chia thành 4 tầng chính:
1. **HTTP Layer:** Route, middleware, controller; xử lý giao tiếp request/response.
2. **Application Layer:** Service/use-case điều phối luồng nghiệp vụ.
3. **Domain Layer:** Entity, domain rule, domain validation.
4. **Infrastructure Layer:** Repository, DB, external API, queue, cache.

## 2. Ranh giới Module & Quy tắc phụ thuộc (Dependency Rules)

### A. HTTP Layer (Route/Controller/Middleware)
File trong `routes/controllers/middlewares/validators` chỉ nên xử lý giao tiếp HTTP và cross-cutting concerns.
* Không đặt business logic dài trong controller.
* Controller không query DB trực tiếp nếu đã có service/repository.
* Middleware tái sử dụng theo chức năng chung, không hardcode domain rule vào middleware generic.

### B. Application & Domain Layer (Service/Use-case)
File trong `services/use-cases/domain/modules` là nơi đặt logic nghiệp vụ.
* Service được phép orchestration transaction, policy, validation nghiệp vụ.
* Không import trực tiếp chi tiết hạ tầng nếu đã có abstraction từ repository/client.
* Tách logic dùng chung thành use-case/helper thay vì copy giữa các module.

### C. Infrastructure Layer (Repository/Client/Model)
File trong `repositories/models/integrations/lib` chịu trách nhiệm truy cập tài nguyên bên ngoài.
* Tất cả DB access đi qua repository để thống nhất transaction, retry và error mapping.
* Tất cả external API call đi qua client/integration layer, không gọi raw request trong service/controller.
* Secret và config nhạy cảm chỉ đọc từ environment config, không hardcode token/key.

## 3. Quy tắc Refactoring cho AI
1. **Bảo toàn hợp đồng API:** Khi refactor route/controller public, không thay đổi request/response shape, status code, auth behavior nếu chưa có yêu cầu rõ ràng.
2. **Single Responsibility:** Mỗi controller/service/repository chỉ nên có một trách nhiệm chính, tách nhỏ khi hàm vượt qua ngưỡng khó đọc.
3. **An toàn dữ liệu:** Mọi thay đổi liên quan transaction, migration, query phải bảo toàn tính đúng dữ liệu và backward compatibility.
4. **Quản lý lỗi nhất quán:** Lỗi domain và lỗi hạ tầng cần được map thống nhất qua error handler, tránh throw raw error ra API.
5. **Không phá vỡ vận hành:** Refactor liên quan logging, metrics, queue, cron, cache phải giữ nguyên hành vi vận hành hiện tại trừ khi có yêu cầu thay đổi.
