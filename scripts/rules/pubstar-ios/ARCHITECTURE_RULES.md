# PubStar iOS SDK — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, luật review của PubStar iOS SDK (Swift, phát hành XCFramework). Căn cứ: 📐 Coding Standards — Mobile SDK (PubStar) v1.0.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.
PR chạm `/core/api`, `/core/handles`, `/core/protocols` (Public API) hoặc luồng mediation trong `/core/adapter`: luôn ghi rõ trong comment tổng kết để người hiểu mediation review lại.

## 1. Tổng quan
Ba tầng (Dependency Inversion): **Public** (những gì app tích hợp thấy) → **Core Domain** (nghiệp vụ SDK) → **Infrastructure/Adapter** (mạng quảng cáo bên thứ ba, network, hệ thống).

## 2. Cấu trúc thư mục & trách nhiệm
- Adapter: `/AdapterGoogle` (Google Mobile Ads), `/AdapterOrtb` (OpenRTB), `/AdapterPrebid`, `/AdapterPubStar` (nội bộ), `/AdpterAppLovin` (AppLovin MAX). Mỗi adapter kế thừa class/protocol trong `/core/base`.
- Public (`public`/`open`): `/core/api` (init, load, show), `/core/handles` (config object app truyền vào), `/core/protocols` (delegate/listener như `AdDelegate`, `RewardListener`).
- Internal (`internal`): `/core/models`, `/core/task` (network request, parse JSON → model), `/core/services` (IDFA, IP, hệ thống), `/core/utils`, `/core/extensions`, `/core/constants`, `/layouts` (render UI native/banner).
- Mediation: `/core/base` (`BaseAdAdapter`/`AdAdapterProtocol`), `/core/adapter` (mediation controller chọn adapter theo waterfall/bidding).
- Cấu hình: `/Enviroments` (Dev/Staging/Prod), `/testmode` (mock/sandbox), `/report` (telemetry, dự kiến).

## 3. Luật review

### 3.1. Public API & access control
- [chặn merge] Đổi/xoá signature public trong `/core/api`, `/core/handles`, `/core/protocols` mà PR không ghi là breaking change có chủ đích.
- [cảnh báo] Thêm requirement vào protocol public không có default implementation.
- [cảnh báo] Type trong `/core/models`, `/core/task`, `/core/services`, `/core/utils`, `/core/extensions`, `/layouts` khai báo `public`/`open`, hoặc lộ ra signature public.
- [cảnh báo] Type trong `/core/api`, `/core/handles`, `/core/protocols` dùng bởi app nhưng không `public`/`open` (app không truy cập được) — CHỈ khi type MỚI.
- [cảnh báo] Logic nghiệp vụ phức tạp đặt trong lớp public thay vì uỷ quyền xuống core.

### 3.2. Adapter & module boundary
- [chặn merge] Adapter import/gọi adapter khác; core gọi trực tiếp class cụ thể của một adapter thay vì qua `/core/base`.
- [cảnh báo] Adapter mới không kế thừa class/protocol trong `/core/base`; adapter giao tiếp ngược về core không qua protocol.
- [cảnh báo] Adapter tự quyết định waterfall/bidding thay vì `/core/adapter`.

### 3.3. Memory, threading
- [chặn merge] Retain cycle: closure lưu lại capture `self` mạnh; delegate không `weak`.
- [chặn merge] Gọi delegate/callback cho app hoặc cập nhật UI ngoài main thread.
- [chặn merge] Timer/observer mới không huỷ khi ad bị destroy/deinit.
- [cảnh báo] Có khả năng gọi callback 2 lần hoặc bỏ sót callback lỗi.

### 3.4. Cấu hình, log, bảo mật
- [chặn merge] Log IDFA/token/credential/PII; credential trong source.
- [cảnh báo] Hardcode URL/endpoint thay vì cấu hình trong `/Enviroments` hoặc `/testmode`.
- [cảnh báo] Log không qua cờ debug của SDK; `print`/`NSLog` trong code phát hành.
- [cảnh báo] Network request đặt ngoài `/core/task`; truy cập hệ thống (IDFA, network info) ngoài `/core/services`.

## 4. Quy ước đặt tên
- [nit] Type PascalCase, method/biến camelCase; protocol listener theo mẫu `XxxDelegate`/`XxxListener`.

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- Tên thư mục `/AdpterAppLovin`, `/Enviroments` sai chính tả là có sẵn; KHÔNG đề xuất đổi tên (ảnh hưởng project/build).
- `/report` mới ở mức dự kiến — không báo "thiếu tracking".

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Không đổi signature public khi refactor `/core/api`. Dùng protocol trong `/core/protocols` để giao tiếp ngược adapter → core.
- Logic URL/endpoint luôn lấy từ `/Enviroments`/`/testmode`. Ưu tiên thay đổi nhỏ.
