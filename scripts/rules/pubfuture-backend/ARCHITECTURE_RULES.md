# PubFuture Backend — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của PubFuture Backend (Node.js + Express). Căn cứ: 📐 Coding Standards — Backend Node.js/Express v1.0.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.
Lưu ý: cấu trúc dưới đây là khung tổng quát; tên thư mục có thể khác trong repo (ví dụ `services` hay `biz`). Khi review, theo pattern của domain gần nhất trong repo; không báo lỗi chỉ vì tên thư mục khác mô tả.

## 1. Tổng quan
Backend tách bạch tầng HTTP, tầng nghiệp vụ và tầng truy cập dữ liệu/hạ tầng.

## 2. Cấu trúc thư mục & trách nhiệm
- Bootstrap: `src/app` hoặc `src/server` (Express app, middleware, global error handler), `src/config` (env, runtime config, feature flag, constant), `src/bootstrap` (khởi tạo dependency, kết nối DB/queue/cache).
- HTTP: `src/routes` (endpoint, nhóm theo domain, versioning), `src/controllers` (parse request → gọi service → trả response), `src/middlewares` (auth, validation, logging, rate limit, request context), `src/validators` (schema đầu vào, không chứa nghiệp vụ).
- Nghiệp vụ: `src/modules` hoặc `src/features` (theo domain), `src/services`/`src/use-cases` (use-case, orchestration), `src/domain` (entity, rule, domain error).
- Dữ liệu & hạ tầng: `src/repositories` (truy vấn DB, map model ↔ domain), `src/models` (schema ORM), `src/integrations`/`src/clients` (API bên thứ ba), `src/lib`/`src/utils` (logger, telemetry, wrapper).
- `tests/` hoặc `src/__tests__`, `scripts/` (migration, seed), `docs/`.

## 3. Luật review

### 3.1. Ranh giới tầng — `route → middleware → validator → controller → service/use-case → repository/client → DB/API ngoài`
- [chặn merge] Controller MỚI query DB/model trực tiếp khi domain đã có service/repository.
- [chặn merge] Service/use-case nhận `req`/`res` của Express hoặc gọi `res.*`.
- [cảnh báo] Logic nghiệp vụ dài (nhiều nhánh, tính toán, phối hợp nhiều nguồn) nằm trong controller.
- [cảnh báo] Service gọi HTTP raw (`axios`/`fetch`) tới bên thứ ba thay vì qua `integrations`/`clients`.
- [cảnh báo] Middleware dùng chung chứa luật nghiệp vụ của một domain.
- [cảnh báo] Copy logic giữa các module thay vì tách use-case/helper dùng chung — CHỈ khi diff hiện cả hai đoạn trùng.

### 3.2. Validate, auth, response, lỗi
- [cảnh báo] Endpoint MỚI nhận input không có validator theo thư viện dự án đang dùng.
- [cảnh báo] Endpoint MỚI thao tác dữ liệu người dùng không có middleware auth như các route cùng domain — dạng câu hỏi nếu không rõ có public không.
- [cảnh báo] Throw raw error/trả lỗi thủ công ra API thay vì để error handler tập trung map lỗi.
- [cảnh báo] Response mới khác format response các endpoint cùng domain.
- [cảnh báo] Đổi request/response shape, status code, auth behavior của API public mà PR không ghi rõ.

### 3.3. Dữ liệu & vận hành
- [chặn merge] Migration mới thiếu `down`; đổi schema bảng đang dùng không backward compatible mà không có kế hoạch.
- [cảnh báo] Ghi nhiều bảng không dùng transaction.
- [cảnh báo] Sửa logging, metrics, queue, cron, cache làm thay đổi hành vi vận hành mà PR không nêu.
- [cảnh báo] Token/key hardcode; đọc `process.env` ngoài `src/config`.

## 4. Quy ước đặt tên
- [nit] File theo domain + vai trò (`user.controller.ts`, `user.service.ts`, `user.repository.ts`), thống nhất với domain gần nhất.

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- (Bổ sung tại đây các chỗ code cũ chưa theo chuẩn và các mẫu báo sai lặp lại mà dev đã xác nhận.)

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Bảo toàn hợp đồng API; giữ hành vi vận hành; ưu tiên thay đổi nhỏ, đúng tầng.
- Mỗi controller/service/repository một trách nhiệm chính; tách nhỏ khi khó đọc.
