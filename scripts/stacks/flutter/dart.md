# Quy tắc Flutter/Dart — chung cho các app Flutter
Nguồn: Coding Standards — Mobile App Flutter v1.0 + CORE + checklist AI review `REVIEW.flutter.md` (mục B). Nhãn: [chặn merge] = MUST · [cảnh báo] = SHOULD · [nit] = NOTE. Khuôn chuẩn: GetX (state) + GetIt (`locator`, DI) + dartz (`Either`) + easy_localization + flutter_gen. Khi luật dự án mô tả lựa chọn khác nhưng nhất quán, theo luật dự án.

## Kiến trúc (Flutter §2–§4) — `presentation → domain ← data`
- [chặn merge] File trong `domain/` import `data/`, `presentation/`, widget Flutter, `dio`, `get` (domain chỉ dùng Dart thuần + `dartz` + `dart:io` + `package:flutter/foundation.dart`).
- [chặn merge] Entity MỚI có `fromJson`/`toJson`, field không `final`, thiếu `@immutable`, hoặc không override `==`/`hashCode`; thêm Equatable/freezed/json_serializable.
- [chặn merge] Presentation (controller/screen/widget) import Model/`data/`/`dio`, gọi `ApiService`/`Dio` hoặc HTTP trực tiếp; Model lọt ra ngoài tầng data.
- [chặn merge] Controller gọi thẳng repository thay vì qua `<x>_usecase`.
- [chặn merge] Repository interface MỚI không trả `Future<Either<Failure, T>>`; repository impl MỚI không bọc `try/catch` → `Left(Failure)`, không kiểm `error_code == 0`, hoặc để exception thoát ra ngoài tầng data.
- [chặn merge] Model parse JSON không ép kiểu tường minh; chuyển Model ↔ Entity ngoài mapper.
- [cảnh báo] Model chứa logic nghiệp vụ/computed getter (Model chỉ lo JSON).

## Presentation, DI, route (Flutter §5–§6)
- [chặn merge] Logic nghiệp vụ hoặc gọi API trong widget; dùng `setState`/StatefulWidget cho state nghiệp vụ.
- [chặn merge] Screen không lấy controller qua `GetBuilder<T>(init: locator<T>())`; dùng `Get.put`/`Get.lazyPut`/Bindings; tự `new` repository/usecase/controller.
- [chặn merge] Đăng ký DI ngoài `initRootGetIt()`, hoặc sai kiểu: controller không phải `registerFactory`; service/repository/usecase không phải `registerLazySingleton`.
- [chặn merge] Controller/State tạo `TextEditingController`, `FocusNode`, `AnimationController`, `StreamSubscription`, `Timer` mà không giải phóng trong `onClose()`/`dispose()`.
- [chặn merge] Dùng `BuildContext` sau `await` trong State/widget mà không kiểm tra `mounted` (hoặc `context.mounted`).
- [chặn merge] Điều hướng bằng chuỗi literal thay vì `RouterName.*`; route MỚI không khai báo `GetPage` (xác minh trước khi báo).
- [chặn merge] Dùng MobX.
- [cảnh báo] Hàm `_buildXxx()` trả Widget thay vì tách widget con; logic nặng hoặc tạo controller/đối tượng nặng trong `build()`.
- [cảnh báo] `Obx` bọc phạm vi quá rộng; nhét object lớn vào một `.obs`; lạm dụng `Get.context!` trong controller.
- [cảnh báo] Widget có thể `const` mà không `const`; dùng `!` tuỳ tiện thay vì xử lý null tường minh.
- [cảnh báo] Không tái dùng widget dùng chung có sẵn (`ButtonWidget`, `Loading`, `CustomSnackBar`, `EmptyState`…).

## Network, UI, i18n (Flutter §7–§9)
- [chặn merge] Tạo `Dio()` ngoài `core/network` (trừ upload pre-signed URL có ghi chú); hardcode URL/endpoint ngoài `app_url.dart`; base URL không đọc từ `.env.$ENV`.
- [chặn merge] `Color(0x...)`/`Colors.*`, `TextStyle(...)` rời, `SizedBox(height: <số tuỳ ý>)` trong widget thay vì `AppColors`/`context.textStyle`/`AppValue`; đường dẫn asset dạng chuỗi thay vì `Assets.*`.
- [chặn merge] Chuỗi hiển thị cho người dùng hardcode thay vì `context.tr(...)`.
- [chặn merge] Key i18n MỚI không có đủ 12 locale — CHỈ báo khi đã xác minh được thư mục locale; không xác minh được thì hỏi ở mức ⚠️.
- [cảnh báo] `Failure.message` hardcode tiếng Anh thay vì key i18n.
- [cảnh báo] `Loading.show()` (hoặc tương đương) không có `hide()` trong `finally`.

## Lỗi, lưu trữ, log (Flutter §10–§12)
- [chặn merge] Nuốt lỗi (`catch (_) {}`); hiển thị exception thô lên UI; không xử lý kết quả bằng `result.fold(...)`; ném `Exception` chung thay vì lớp con `Failure`.
- [chặn merge] Lưu token/secret bằng Hive/SharedPreferences thay vì secure storage; logout không dọn cả secure storage lẫn Hive; mở Hive box rải rác.
- [chặn merge] `LogInterceptor`/`CurlLoggerDioInterceptor` có thể bật ở production; log token/mật khẩu/PII.
- [chặn merge] `print()`/`debugPrint()` trong code production; `// ignore:` không ghi lý do; dùng thêm SHA-1/MD5.

## Test & công cụ (Flutter §13)
- [chặn merge] Usecase/repository impl/mapper MỚI hoặc bug fix không có test — điều kiện xác minh theo mục "Về việc THIẾU test" của `core.md`; test controller GetX thiếu `Get.testMode = true`/`tearDown(Get.reset)`; dùng mocktail hoặc mock tay thay vì `@GenerateMocks`. Chi tiết: `flutter/testing.md`.
- [cảnh báo] Feature mới không tạo bằng `feature_cli` (cấu trúc thư mục lệch khuôn).
