# Quy tắc Flutter/Dart — chung cho các app Flutter
Nguồn: Coding Standards — Mobile App Flutter v1.0 + CORE. Thư viện cụ thể (GetX, GetIt, dartz, easy_localization, flutter_gen) theo luật dự án; khi dự án dùng lựa chọn khác nhưng nhất quán, theo luật dự án.

## Kiến trúc (Flutter §2–§4) — `presentation → domain ← data`
- [chặn merge] File trong `domain/` import `data/`, `presentation/`, widget Flutter, `dio`, `get` (domain chỉ dùng Dart thuần + `dartz` + `package:flutter/foundation.dart`).
- [chặn merge] Presentation (controller/screen/widget) import `data/models/`, gọi `ApiService`/`Dio` hoặc HTTP trực tiếp.
- [cảnh báo] Entity MỚI có `fromJson`/`toJson`, field không `final`, thiếu `@immutable`.
- [cảnh báo] Model chứa logic nghiệp vụ/computed getter (Model chỉ lo JSON).
- [cảnh báo] Repository impl trả Model ra ngoài thay vì map sang Entity qua mapper; chuyển Model ↔ Entity ngoài mapper.
- [cảnh báo] Repository interface MỚI không trả `Future<Either<Failure, T>>` (khi dự án dùng dartz).
- [cảnh báo] Repository impl MỚI không bọc `try/catch` để trả `Left(Failure)` — exception thoát ra ngoài tầng data.
- [nit] Controller gọi thẳng repository khi feature đã có usecase cho thao tác đó.

## Presentation, state & DI (Flutter §5–§6)
- [chặn merge] Controller/State tạo `TextEditingController`, `FocusNode`, `AnimationController`, `StreamSubscription`, `Timer` mà không giải phóng trong `onClose()`/`dispose()`.
- [chặn merge] Dùng `BuildContext` sau `await` trong State/widget mà không kiểm tra `mounted` (hoặc `context.mounted`).
- [cảnh báo] Logic nghiệp vụ hoặc gọi API trong widget/`build()`; tạo controller/đối tượng nặng trong `build()`.
- [cảnh báo] Lấy/đăng ký dependency khác cơ chế DI của dự án (ví dụ dùng `Get.put`/`Get.lazyPut` khi dự án dùng GetIt; tự `new` repository/usecase trong widget).
- [cảnh báo] Điều hướng bằng chuỗi literal thay vì hằng route của dự án (ví dụ `RouterName.*`).
- [nit] `Obx` bọc phạm vi quá rộng; nhét object lớn vào một `.obs`.
- [nit] Hàm `_buildXxx()` trả Widget lớn thay vì tách widget con; widget có thể `const` mà không `const`.

## UI, i18n, asset (Flutter §8–§9)
- [cảnh báo] Chuỗi hiển thị cho người dùng hardcode thay vì `context.tr(...)`/cơ chế i18n của dự án.
- [cảnh báo] Key i18n MỚI không được thêm vào đủ các file locale — CHỈ báo khi đã xác minh được thư mục locale; không xác minh được thì hỏi.
- [cảnh báo] `Color(0x...)`/`Colors.*`, `TextStyle(...)` rời, khoảng cách số tuỳ ý trong widget thay vì `AppColors`/`context.textStyle`/`AppValue` của dự án.
- [cảnh báo] Đường dẫn asset dạng chuỗi (`'assets/...'`) khi dự án dùng `flutter_gen` (`Assets.*`).

## Network, lỗi, lưu trữ, log (Flutter §7, §10–§12)
- [chặn merge] Lưu token/secret bằng SharedPreferences/Hive thay vì secure storage.
- [chặn merge] Log token, mật khẩu, PII; bật `LogInterceptor`/curl logger mà không giới hạn ở môi trường debug.
- [cảnh báo] Tạo `Dio()` mới ngoài module network của dự án; hardcode URL/endpoint ngoài file URL/config.
- [cảnh báo] Nuốt lỗi (`catch (_) {}`); hiển thị exception thô lên UI; không xử lý cả nhánh lỗi của `Either` (`fold`).
- [cảnh báo] `print()`/`debugPrint()` trong code production thay vì logger; `// ignore:` không ghi lý do.
- [cảnh báo] `Loading.show()` (hoặc tương đương) không có `hide()` trong `finally`.
- [nit] Dùng `!` tuỳ tiện thay vì xử lý null tường minh.

## Test (Flutter §13)
- [nit] Usecase/repository impl/mapper MỚI hoặc bug fix không có test — dạng câu hỏi.
