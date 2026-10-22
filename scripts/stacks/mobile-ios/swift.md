# Quy tắc iOS (Swift) — SDK và app iOS
Nguồn: Coding Standards — Mobile SDK (PubStar) §1, §4 + CORE. Mục "Public API" CHỈ áp dụng cho dự án là SDK/framework publish.

## Public API & access control — CHỈ áp dụng cho SDK/framework
- [chặn merge] Đổi/xoá signature `public`/`open` (tên, tham số, label, kiểu trả về, protocol requirement) mà PR không ghi là breaking change có chủ đích (major version + changelog). [📐 SDK §1.1]
- [cảnh báo] Thêm requirement mới vào protocol public mà không có default implementation qua extension (làm gãy app đang conform). [📐 SDK §1.1]
- [cảnh báo] Đổi type nội bộ (model, task, service, util) thành `public`/`open`; type nội bộ lộ ra trong signature public. [📐 SDK §4.1]
- [cảnh báo] Public API `throw`/`fatalError` ra app tích hợp khi không phải dùng sai rõ ràng; lỗi không trả qua delegate/closure kèm error code. [📐 SDK §1.4]
- [nit] Class public không cần kế thừa từ bên ngoài nhưng khai báo `open` thay vì `public final`. [📐 SDK §4.1]

## Memory & concurrency
- [chặn merge] Closure lưu lại (completion lưu thành property, timer, observer, network callback) capture `self` mạnh tạo retain cycle — dùng `[weak self]`. [📐 SDK §4.2; SDK §1.3]
- [chặn merge] Delegate khai báo `strong` (phải `weak var delegate`). [📐 SDK §4.2; SDK §1.3]
- [chặn merge] Cập nhật UI hoặc gọi delegate/callback cho app từ background thread mà không chuyển về main thread. [📐 SDK §1.3]
- [chặn merge] `Timer`, `NotificationCenter` observer, KVO, `DispatchSourceTimer` MỚI không được huỷ/remove khi đối tượng giải phóng hoặc ad bị destroy. [📐 SDK §1.3]
- [cảnh báo] Truy cập state dùng chung từ nhiều queue mà không có serial queue/lock/actor. [📐 SDK §1.3]
- [cảnh báo] Có khả năng gọi callback/completion 2 lần hoặc không gọi ở một nhánh lỗi. [📐 SDK §1.3]

## Swift
- [cảnh báo] Force unwrap `!`, `try!`, `as!` trên dữ liệu từ server/JSON/người dùng hoặc giá trị diff cho thấy có thể nil. [📐 SDK §4.2]
- [cảnh báo] `catch` rỗng hoặc chỉ `print(error)`. [📐 SDK §1.4; Core §1.2]
- [nit] `var` cho giá trị không đổi; `class` cho kiểu dữ liệu thuần có thể là `struct`. [Dự án]

## Log, cấu hình, bảo mật
- [chặn merge] Log IDFA, token, credential, PII; log không đi qua cờ debug của SDK; `print`/`NSLog` trong code production. [📐 SDK §1.4; Core §7]
- [chặn merge] Credential/API key trong source. [📐 SDK §1.5; Core §5]
- [cảnh báo] Hardcode URL/endpoint thay vì cấu hình môi trường của dự án. [📐 SDK §1.5]
- [cảnh báo] Lưu token/secret vào `UserDefaults` thay vì Keychain. [📐 Core §5]
