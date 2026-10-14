# Quy tắc Android (Kotlin/Java) — SDK và app Android
Nguồn: Coding Standards — Mobile SDK (PubStar) §1, §3 + CORE. Mục "Public API" CHỈ áp dụng cho dự án là SDK/thư viện publish.

## Public API & tương thích (SDK §1.1) — CHỈ áp dụng cho SDK/thư viện
- [chặn merge] Đổi/xoá package, class, method, tham số hoặc kiểu trả về public mà PR không ghi là breaking change có chủ đích (major version + changelog).
- [cảnh báo] Type internal lộ ra trong signature public; đổi class internal thành `public` để gọi chéo module (Kotlin mặc định `internal`, Java package-private).
- [cảnh báo] Thêm API mới bằng cách sửa signature cũ thay vì overload/builder + `@Deprecated`.
- [cảnh báo] Public API ném exception ra app tích hợp khi không phải dùng sai rõ ràng; lỗi không trả qua callback kèm error code.

## Ranh giới module (SDK §2)
- [chặn merge] Module core phụ thuộc module adapter/plugin; adapter phụ thuộc adapter khác.
- [cảnh báo] Core import SDK quảng cáo/bên thứ 3 mà logic riêng network đó phải nằm ở adapter.

## Threading & lifecycle (SDK §1.3)
- [chặn merge] Giữ `Activity`/`Fragment`/`View`/`Context` không phải application trong field static, singleton hoặc callback sống lâu hơn lifecycle.
- [chặn merge] Network/disk I/O trên main thread (`runBlocking` trên main, gọi HTTP đồng bộ trong callback UI).
- [chặn merge] `Handler.postDelayed`, `Timer`, coroutine `Job`, listener MỚI không được huỷ khi destroy/clear.
- [cảnh báo] Cập nhật UI/callback cho app từ background thread mà không chuyển về main thread.
- [cảnh báo] `GlobalScope.launch` thay vì scope gắn lifecycle/scope của SDK.
- [cảnh báo] Có khả năng gọi callback 2 lần (load/show không có cờ trạng thái).
- [cảnh báo] Truy cập state dùng chung từ nhiều thread mà không `synchronized`/`Atomic*`/`Mutex`.

## Kotlin
- [cảnh báo] `!!` trên giá trị mà diff cho thấy có thể null (kết quả `find`, `get`, field nullable vừa gán).
- [cảnh báo] `catch (e: Exception) {}` rỗng hoặc chỉ `printStackTrace()`.
- [nit] `var` cho giá trị không đổi; `lateinit` cho field có thể chưa khởi tạo khi được dùng.

## Log, cấu hình, bảo mật (SDK §1.4–§1.6)
- [chặn merge] Log PII, credential, token, GAID; log không đi qua cờ debug/`isShowLog` của dự án.
- [chặn merge] Credential/API key trong source.
- [cảnh báo] Hardcode URL/endpoint production thay vì `BuildConfig`/`local.properties`/cấu hình.
- [cảnh báo] Commit output build (`*/build/`, `BuildConfig.java`, `R.jar`, `R.txt`).

## Proguard/R8 & resource (SDK §1.5)
- [cảnh báo] Xoá keep rule đang dùng; class dùng reflection/được SDK ngoài gọi MỚI mà không có keep rule (ưu tiên `consumer-rules.pro` của đúng module).
- [cảnh báo] Đổi/xoá resource id public mà app tích hợp có thể tham chiếu.
- [nit] Dependency bên thứ 3 dùng `implementation` khi `compileOnly` phù hợp hơn cho thư viện publish.
