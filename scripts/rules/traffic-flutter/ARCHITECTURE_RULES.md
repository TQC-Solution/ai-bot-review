# Traffic Flutter — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của app Flutter team Traffic (Clean Architecture + GetX). Căn cứ: 📐 Coding Standards — Mobile App Flutter v1.0.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.
Nguyên tắc vàng: Domain là trung tâm, Domain KHÔNG phụ thuộc ai — `Presentation → Domain ← Data`.

## 1. Cấu trúc 3 layer theo feature
```
feature/
├── domain/       entities/ (business object thuần) · repositories/ (interface trả Entity) · usecases/ (tuỳ chọn cho CRUD đơn giản)
├── data/         models/ (DTO, chỉ JSON) · mappers/ (Model ↔ Entity) · repositories/ (*_repository_impl.dart)
└── presentation/ controllers/ (GetxController, state .obs, dùng Entity) · screens/ (*_screen.dart) · widgets/ (*_widget.dart)
```
| Layer | Chứa | KHÔNG chứa | Trả về |
|---|---|---|---|
| Domain | business logic, interface | JSON, API, DB | Entity |
| Data | JSON, API, DB, mapper | business logic | Entity (sau map) |
| Presentation | UI, state | business logic, API trực tiếp | — |

- Entity: Dart thuần, `@immutable`, field `final`, có thể chứa computed getter/validation (ví dụ `fullImageUrl`, `isValid`).
- Repository interface: `Future<Either<Failure, Entity>>` (dartz). Repository impl: gọi API → parse Model → map sang Entity → `Right(...)`; lỗi → `Left(ServerFailure(...))`.
- Controller: gọi repository/usecase, `result.fold(...)`, feedback qua `CustomSnackBar`; `Loading.show()`/`Loading.hide()` trong `finally`.
- Tiện ích: asset qua `flutter_gen` (`Assets.icons.*`); i18n `easy_localization` (`context.tr('settings.language')`, key snake_case phân cấp: `app.*`, `common.*`, `auth.*`, `settings.*`, `validation.*`, `messages.*`); style `context.textStyle.bodyLG.medium`, `AppValue.hSpaceSmall`, `AppColors.bgrPrimary`; điều hướng `Get.toNamed(RouterName.home)`; DI trong `service_locator.dart`; dòng tối đa 80 ký tự.

## 2. Luật review

### 2.1. Dependency rule
- [chặn merge] File trong `domain/` import `data/` hoặc `presentation/`. [📐 Flutter §2]
- [chặn merge] Presentation import `data/models/`, dùng Model, mapper hoặc `ApiService`. [📐 Flutter §2]
- [chặn merge] Controller gọi API trực tiếp thay vì repository/usecase. [📐 Flutter §2]

### 2.2. Domain & data
- [cảnh báo] Entity có `fromJson`/`toJson`; field không `final`; thiếu `@immutable`. [📐 Flutter §3]
- [cảnh báo] Model có business logic/computed getter. [📐 Flutter §4]
- [cảnh báo] Repository impl trả Model thay vì Entity; map Model → Entity ngoài mapper. [📐 Flutter §4]
- [cảnh báo] Repository interface/impl mới không trả `Either<Failure, T>`; impl không bọc try/catch → `Left(Failure)`; throw raw exception ra UI. [📐 Flutter §4; Flutter §10]

### 2.3. Presentation
- [chặn merge] Controller tạo `TextEditingController`/`FocusNode`/subscription/`Timer` không giải phóng trong `onClose()`. [📐 Flutter §5]
- [cảnh báo] Controller không xử lý nhánh lỗi của `fold` (bỏ qua failure). [📐 Flutter §10]
- [cảnh báo] `Loading.show()` không có `Loading.hide()` trong `finally`. [📐 Flutter §10]
- [cảnh báo] Điều hướng bằng chuỗi literal thay vì `RouterName.*`. [📐 Flutter §6]
- [cảnh báo] Đăng ký dependency ngoài `service_locator.dart` hoặc tự `new` repository/usecase trong controller/widget. [📐 Flutter §6]
- [nit] Widget nhận Model hoặc dữ liệu thô thay vì Entity. [📐 Flutter §2]

### 2.4. Coding standards
- [cảnh báo] Hardcode asset path (`'assets/...'`) thay vì `Assets.*`. [📐 Flutter §8]
- [cảnh báo] Text hiển thị hardcode thay vì `context.tr(...)`; key i18n mới không thêm đủ các file locale — CHỈ báo khi xác minh được. [📐 Flutter §9]
- [cảnh báo] `Color(0x...)`/`Colors.*`, `TextStyle(...)` rời, `SizedBox` với số tuỳ ý thay vì `AppColors`/`context.textStyle`/`AppValue`. [📐 Flutter §9]
- [cảnh báo] `print()` trong code; log token/PII; lưu token bằng SharedPreferences/Hive thay vì secure storage. [📐 Flutter §8; Flutter §12]
- [nit] File/class/method không theo quy ước §3. [📐 Flutter §8; Core §2]

### 2.5. Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.
- [cảnh báo] Repository impl mới mà test không có đủ: `res['success'] == true` → `Right` qua mapper; `success != true` → `Left(ServerFailure)`; exception → `Left`. [📐 Test Flutter §7.1]
- [nit] Test mapper không có case field null/thiếu. [📐 Test Flutter §7.1]

## 3. Quy ước đặt tên
- File snake_case: `*_screen.dart`, `*_controller.dart`, `*_widget.dart`, `dialog_*.dart`, `*_entity.dart`, `*_model.dart`/`*_response.dart`, `*_usecase.dart`, `*_repository.dart`/`*_repository_impl.dart`, `*_mapper.dart`.
- Class PascalCase (`SettingScreen`, `SettingController`, `UserModel`, `SettingRepositoryImpl`); biến/method camelCase, method bắt đầu bằng động từ (`onTapLanguage()`, `updateUserStatus()`); private có `_`.

## 4. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- Usecase là tuỳ chọn cho CRUD đơn giản: KHÔNG báo controller gọi repository trực tiếp khi feature không có usecase.
- (Bổ sung tại đây các mẫu báo sai lặp lại mà dev đã xác nhận.)

## 5. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Model chỉ biết JSON · Entity chỉ biết business · Mapper là cầu nối bắt buộc · Repository luôn trả Entity · Presentation không biết Model tồn tại.
- Tự kiểm tra: `grep -r "import.*data/" lib/**/domain/`, `grep -r "import.*data/models/" lib/**/presentation/`, `grep -r "fromJson\|toJson" lib/**/domain/entities/` phải rỗng.
