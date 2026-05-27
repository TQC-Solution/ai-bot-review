# Flutter Architecture Rules — traffic-flutter

Clean Architecture + GetX. Đây là quy tắc kiến trúc và coding để review code.
**Nguyên tắc vàng: Domain là trung tâm, Domain KHÔNG phụ thuộc ai.**

---

## 1. Dependency Rule

```
Presentation ──→ Domain ←── Data
```

- **Presentation** → import **Domain** ✅ | import **Data** ❌
- **Data** → import **Domain** (interfaces) ✅
- **Domain** → import **Data** / **Presentation** ❌ **VI PHẠM**

Chiều mũi tên = chiều phụ thuộc. Domain không bao giờ import ra ngoài.

---

## 2. Cấu trúc 3 Layer

```
feature/
├── domain/
│   ├── entities/        # Business object thuần (KHÔNG fromJson/toJson)
│   ├── repositories/    # Interface (abstract), trả về Entity
│   └── usecases/        # Business logic phức tạp (optional cho CRUD đơn giản)
├── data/
│   ├── models/          # DTO, CHỈ JSON serialization
│   ├── mappers/         # Convert Model ↔ Entity
│   └── repositories/    # *_repository_impl.dart, map Model→Entity rồi return
└── presentation/
    ├── controllers/     # GetxController, state bằng .obs, dùng Entity
    ├── screens/         # *_screen.dart
    └── widgets/         # *_widget.dart, nhận Entity
```

| Layer | Chứa | KHÔNG chứa | Return |
|-------|------|------------|--------|
| Domain | Business logic, interfaces | JSON, API, DB | Entities |
| Data | JSON, API, DB, Mapper | Business logic | Entities (sau map) |
| Presentation | UI, state | Business logic, API trực tiếp | — |

---

## 3. Quy tắc mỗi Layer

### Domain
- Entity: pure Dart, `@immutable`, `final` fields, chứa **business logic** (computed getter, validation). **KHÔNG** `fromJson`/`toJson`.
- Repository interface trả về `Future<Either<Failure, Entity>>`, không bao giờ Model.

```dart
@immutable
class Novel {
  const Novel({required this.id, required this.coverImage});
  final String id;
  final String coverImage;

  String get fullImageUrl =>
      coverImage.startsWith('http') ? coverImage : '${AppUrl.urlImage}$coverImage';
  bool get isValid => id.isNotEmpty;
}

abstract class HomeRepository {
  Future<Either<Failure, List<Novel>>> getHotNovels({int? page});
}
```

### Data
- Model: CHỈ `fromJson`/`toJson`. **KHÔNG** business logic, computed getter.
- Mapper: cầu nối bắt buộc, convert Model → Entity (và ngược lại nếu cần).
- Repository impl: gọi API → parse Model → **map sang Entity** → return Entity.

```dart
class HomeRepositoryImpl implements HomeRepository {
  HomeRepositoryImpl(this._api);
  final ApiService _api;

  @override
  Future<Either<Failure, List<Novel>>> getHotNovels({int? page}) async {
    try {
      final res = await _api.post(AppUrl.hotNovels, data: {'page': page});
      if (res['success'] == true) {
        final models = NovelModel.fromJsonList(res['data']);
        return Right(NovelMapper.toEntityList(models)); // map trước khi return
      }
      return Left(ServerFailure(message: res['message']));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }
}
```

### Presentation
- Controller import Domain, dùng Entity với `.obs`, gọi repository/usecase — **KHÔNG** gọi API trực tiếp, không dùng Model, không mapper.
- Widget nhận Entity, dùng business logic từ Entity.

```dart
class HomeController extends GetxController {
  HomeController(this._repo);
  final HomeRepository _repo;
  final RxList<Novel> hotNovels = <Novel>[].obs;

  Future<void> loadHotNovels() async {
    final result = await _repo.getHotNovels(page: 1);
    result.fold(
      (f) => CustomSnackBar.showError(message: f.message),
      (novels) => hotNovels.assignAll(novels),
    );
  }
}
```

---

## 4. Vi phạm phổ biến (BLOCK / WARN)

| # | Vi phạm | Sửa |
|---|---------|-----|
| 1 | Model có business logic / computed getter | Chuyển logic sang Entity |
| 2 | Entity có `fromJson`/`toJson` | Bỏ JSON, để ở Model |
| 3 | Presentation import `data/models/` | Dùng Entity từ domain |
| 4 | Repository impl trả về Model | Map Model → Entity rồi return |
| 5 | Domain import `data/` hoặc `presentation/` | Chỉ import trong domain |
| 6 | Controller gọi API trực tiếp / dùng ApiService | Gọi qua repository/usecase |

Lệnh tự kiểm tra:
```bash
grep -r "import.*data/" lib/**/domain/                 # phải rỗng
grep -r "import.*data/models/" lib/**/presentation/     # phải rỗng
grep -r "fromJson\|toJson" lib/**/domain/entities/      # phải rỗng
```

---

## 5. Naming Conventions

**File (snake_case):** `*_screen.dart`, `*_controller.dart`, `*_widget.dart`, `dialog_*.dart`,
`*_entity.dart` / `*.dart` (core entity), `*_model.dart` / `*_response.dart`, `*_usecase.dart`,
`*_repository.dart` / `*_repository_impl.dart`, `*_mapper.dart`.

**Class (PascalCase):** `SettingScreen`, `SettingController`, `ButtonWidget`, `AuthEntity`,
`UserModel`, `SettingRepository` / `SettingRepositoryImpl`.

**Biến & method (camelCase):** `isLoading`, `userName`, observable `isEnabled.obs`,
private `_apiService`, method verb-first `onTapLanguage()`, `updateUserStatus()`, `validateEmail()`.

---

## 6. Coding Standards

### Assets — type-safe với flutter_gen
```dart
SvgPicture.asset(Assets.icons.iconBack)        // ✅
Image.asset('assets/images/logo.png')          // ❌ hardcode path
```

### Localization — easy_localization, key snake_case phân cấp
```dart
Text(context.tr('settings.language'))                                 // ✅
Text(context.tr('auth.welcome_user', namedArgs: {'name': userName}))  // interpolation
Text('Settings')                                                      // ❌ hardcode
```
Categories: `app.*`, `common.*`, `auth.*`, `settings.*`, `validation.*`, `messages.*`.

### Error Handling — `Either<Failure, T>` (package dartz)
- Repository trả về `Either<Failure, T>` với Failure type cụ thể (`ServerFailure`, `NetworkException`, `ServerTimeOut`…). **KHÔNG** throw raw exception ra UI.
- Controller xử lý cả `failure` lẫn success trong `.fold()`, feedback qua `CustomSnackBar`.
- Bọc async bằng `Loading.show()` / `Loading.hide()` trong `finally`.

```dart
Future<void> deleteAccount() async {
  Loading.show();
  try {
    final result = await useCase.deleteAccount();
    result.fold(
      (f) => CustomSnackBar.showError(message: f.message),
      (_) => Get.offAllNamed(RouterName.signIn),
    );
  } finally {
    Loading.hide();
  }
}
```

### Style & Spacing
- Text: `context.textStyle.bodyLG.medium`, `.headingMD.bold.textPrimary`.
- Spacing: `AppValue.hSpaceSmall`, `AppValue.vSpaceSmall`, `AppValue.hSpace(12)`.
- Colors: `AppColors.bgrPrimary`. Router: `Get.toNamed(RouterName.home)`.
- Line length 80 chars.

---

## 7. Checklist Review

**Domain:** không import data/presentation · entity không JSON · entity chỉ business logic · interface trả Entity.
**Data:** model chỉ JSON · model không business logic · impl dùng mapper · impl trả Entity sau map.
**Presentation:** import domain · dùng Entity · widget nhận Entity · gọi repository/usecase (không API trực tiếp).
**Coding:** asset type-safe · text qua `context.tr()` · `Either<Failure,T>` · Loading có hide trong finally · naming nhất quán · DI trong `service_locator.dart`.

> Model chỉ biết JSON · Entity chỉ biết business · Mapper là cầu nối bắt buộc · Repository luôn trả Entity · Presentation quên Model tồn tại.
