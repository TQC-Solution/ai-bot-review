# Quy tắc Flutter/Dart — chung cho các app Flutter
Nguồn: Coding Standards — Mobile App Flutter v1.0 + CORE. Thư viện cụ thể (GetX, GetIt, dartz, easy_localization, flutter_gen) theo luật dự án; khi dự án dùng lựa chọn khác nhưng nhất quán, theo luật dự án.

## Kiến trúc — `presentation → domain ← data`
- [chặn merge] File trong `domain/` import `data/`, `presentation/`, widget Flutter, `dio`, `get` (domain chỉ dùng Dart thuần + `dartz` + `package:flutter/foundation.dart`). [📐 Flutter §2]
- [chặn merge] Presentation (controller/screen/widget) import `data/models/`, gọi `ApiService`/`Dio` hoặc HTTP trực tiếp. [📐 Flutter §2]
- [cảnh báo] Entity MỚI có `fromJson`/`toJson`, field không `final`, thiếu `@immutable`. [📐 Flutter §3]
- [cảnh báo] Model chứa logic nghiệp vụ/computed getter (Model chỉ lo JSON). [📐 Flutter §4]
- [cảnh báo] Repository impl trả Model ra ngoài thay vì map sang Entity qua mapper; chuyển Model ↔ Entity ngoài mapper. [📐 Flutter §4]
- [cảnh báo] Repository interface MỚI không trả `Future<Either<Failure, T>>` (khi dự án dùng dartz). [📐 Flutter §2]
- [cảnh báo] Repository impl MỚI không bọc `try/catch` để trả `Left(Failure)` — exception thoát ra ngoài tầng data. [📐 Flutter §4]
- [nit] Controller gọi thẳng repository khi feature đã có usecase cho thao tác đó. [📐 Flutter §2]

## Presentation, state & DI
- [chặn merge] Controller/State tạo `TextEditingController`, `FocusNode`, `AnimationController`, `StreamSubscription`, `Timer` mà không giải phóng trong `onClose()`/`dispose()`. [📐 Flutter §5]
- [chặn merge] Dùng `BuildContext` sau `await` trong State/widget mà không kiểm tra `mounted` (hoặc `context.mounted`). [📐 Flutter §8]
- [cảnh báo] Logic nghiệp vụ hoặc gọi API trong widget/`build()`; tạo controller/đối tượng nặng trong `build()`. [📐 Flutter §5]
- [cảnh báo] Lấy/đăng ký dependency khác cơ chế DI của dự án (ví dụ dùng `Get.put`/`Get.lazyPut` khi dự án dùng GetIt; tự `new` repository/usecase trong widget). [📐 Flutter §6; Flutter §5]
- [cảnh báo] Điều hướng bằng chuỗi literal thay vì hằng route của dự án (ví dụ `RouterName.*`). [📐 Flutter §6]
- [nit] `Obx` bọc phạm vi quá rộng; nhét object lớn vào một `.obs`. [📐 Flutter §6]
- [nit] Hàm `_buildXxx()` trả Widget lớn thay vì tách widget con; widget có thể `const` mà không `const`. [📐 Flutter §8]

## UI, i18n, asset
- [cảnh báo] Chuỗi hiển thị cho người dùng hardcode thay vì `context.tr(...)`/cơ chế i18n của dự án. [📐 Flutter §9]
- [cảnh báo] Key i18n MỚI không được thêm vào đủ các file locale — CHỈ báo khi đã xác minh được thư mục locale; không xác minh được thì hỏi. [📐 Flutter §9]
- [cảnh báo] `Color(0x...)`/`Colors.*`, `TextStyle(...)` rời, khoảng cách số tuỳ ý trong widget thay vì `AppColors`/`context.textStyle`/`AppValue` của dự án. [📐 Flutter §9]
- [cảnh báo] Đường dẫn asset dạng chuỗi (`'assets/...'`) khi dự án dùng `flutter_gen` (`Assets.*`). [📐 Flutter §8]

## Network, lỗi, lưu trữ, log
- [chặn merge] Lưu token/secret bằng SharedPreferences/Hive thay vì secure storage. [📐 Flutter §12]
- [chặn merge] Log token, mật khẩu, PII; bật `LogInterceptor`/curl logger mà không giới hạn ở môi trường debug. [📐 Flutter §12]
- [cảnh báo] Tạo `Dio()` mới ngoài module network của dự án; hardcode URL/endpoint ngoài file URL/config. [📐 Flutter §7]
- [cảnh báo] Nuốt lỗi (`catch (_) {}`); hiển thị exception thô lên UI; không xử lý cả nhánh lỗi của `Either` (`fold`). [📐 Flutter §10]
- [cảnh báo] `print()`/`debugPrint()` trong code production thay vì logger; `// ignore:` không ghi lý do. [📐 Flutter §8]
- [cảnh báo] `Loading.show()` (hoặc tương đương) không có `hide()` trong `finally`. [📐 Flutter §10]
- [nit] Dùng `!` tuỳ tiện thay vì xử lý null tường minh. [📐 Flutter §8]

## Test
- Luật về unit test: xem `flutter/testing.md`.
