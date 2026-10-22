# Quy tắc Android (Kotlin/Java) — SDK và app Android
Nguồn: Coding Standards — Mobile SDK (PubStar) §1, §3 + CORE. Mục "Public API" CHỈ áp dụng cho dự án là SDK/thư viện publish.

## Public API & tương thích — CHỈ áp dụng cho SDK/thư viện
- [chặn merge] Đổi/xoá package, class, method, tham số hoặc kiểu trả về public mà PR không ghi là breaking change có chủ đích (major version + changelog). [📐 SDK §1.1]
- [cảnh báo] Type internal lộ ra trong signature public; đổi class internal thành `public` để gọi chéo module (Kotlin mặc định `internal`, Java package-private). [📐 SDK §3.2; SDK §1.2]
- [cảnh báo] Thêm API mới bằng cách sửa signature cũ thay vì overload/builder + `@Deprecated`. [📐 SDK §1.1]
- [cảnh báo] Public API ném exception ra app tích hợp khi không phải dùng sai rõ ràng; lỗi không trả qua callback kèm error code. [📐 SDK §1.4]

## Ranh giới module
- [chặn merge] Module core phụ thuộc module adapter/plugin; adapter phụ thuộc adapter khác. [📐 SDK §3.4; SDK §2]
- [cảnh báo] Core import SDK quảng cáo/bên thứ 3 mà logic riêng network đó phải nằm ở adapter. [📐 SDK §3.4; SDK §2]

## Threading & lifecycle
- [chặn merge] Giữ `Activity`/`Fragment`/`View`/`Context` không phải application trong field static, singleton hoặc callback sống lâu hơn lifecycle. [📐 SDK §3.5; SDK §1.3]
- [chặn merge] Network/disk I/O trên main thread (`runBlocking` trên main, gọi HTTP đồng bộ trong callback UI). [📐 SDK §3.5]
- [chặn merge] `Handler.postDelayed`, `Timer`, coroutine `Job`, listener MỚI không được huỷ khi destroy/clear. [📐 SDK §1.3]
- [cảnh báo] Cập nhật UI/callback cho app từ background thread mà không chuyển về main thread. [📐 SDK §3.5]
- [cảnh báo] `GlobalScope.launch` thay vì scope gắn lifecycle/scope của SDK. [📐 SDK §3.5]
- [cảnh báo] Có khả năng gọi callback 2 lần (load/show không có cờ trạng thái). [📐 SDK §1.3]
- [cảnh báo] Truy cập state dùng chung từ nhiều thread mà không `synchronized`/`Atomic*`/`Mutex`. [📐 SDK §3.5]

## Kotlin
- [cảnh báo] `!!` trên giá trị mà diff cho thấy có thể null (kết quả `find`, `get`, field nullable vừa gán). [Dự án]
- [cảnh báo] `catch (e: Exception) {}` rỗng hoặc chỉ `printStackTrace()`. [📐 SDK §1.4; Core §1.2]
- [nit] `var` cho giá trị không đổi; `lateinit` cho field có thể chưa khởi tạo khi được dùng. [Dự án]

## Log, cấu hình, bảo mật
- [chặn merge] Log PII, credential, token, GAID; log không đi qua cờ debug/`isShowLog` của dự án. [📐 SDK §1.4; Core §7]
- [chặn merge] Credential/API key trong source. [📐 SDK §1.5; Core §5]
- [cảnh báo] Hardcode URL/endpoint production thay vì `BuildConfig`/`local.properties`/cấu hình. [📐 SDK §3.6; SDK §1.5]
- [cảnh báo] Commit output build (`*/build/`, `BuildConfig.java`, `R.jar`, `R.txt`). [📐 SDK §1.5; Core §6.1]

## Proguard/R8 & resource
- [cảnh báo] Xoá keep rule đang dùng; class dùng reflection/được SDK ngoài gọi MỚI mà không có keep rule (ưu tiên `consumer-rules.pro` của đúng module). [📐 SDK §3.6]
- [cảnh báo] Đổi/xoá resource id public mà app tích hợp có thể tham chiếu. [📐 SDK §1.6; SDK §1.1]
- [nit] Dependency bên thứ 3 dùng `implementation` khi `compileOnly` phù hợp hơn cho thư viện publish. [📐 SDK §1.2]
