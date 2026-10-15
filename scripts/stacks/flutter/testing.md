# Quy tắc unit test — Flutter (flutter_test + mockito)
Nguồn: [TECH] Test Standard — Mobile Flutter v1.0. Bổ sung cho mục Test trong `core.md`. KHÔNG áp dụng khi luật dự án ghi dự án chưa có test framework.

Bối cảnh chuẩn: `flutter_test` + mockito (`@GenerateMocks`/`@GenerateNiceMocks`, sinh bằng `dart run build_runner build`); thư mục `test/` phản chiếu `lib/` theo feature và tầng; một file test cho một file source, tên `<tên_file_source>_test.dart`; `*.mocks.dart` nằm cạnh file test; fixture ở `test/fixtures/`. Coverage tối thiểu: tổng 70% · domain/logic (usecase, repo, mapper) 75% · widget quan trọng 60%.

## Thiếu test (§3.2, §7.1)
- [chặn merge] Usecase, repository impl, mapper MỚI mà PR không có file test tương ứng — CHỈ khi xác minh được danh sách file của PR; không xác minh được thì hỏi ở mức ⚠️. (REVIEW.flutter.md — Flutter §13)
- [nit] Test có trong diff nhưng thiếu case tối thiểu (CHỈ khi nhìn thấy toàn bộ test của đơn vị đó):
  - Validator/util: input hợp lệ; MỖI loại input không hợp lệ; rỗng/null.
  - Usecase: `Right(entity)` khi repo thành công; `Left(Failure)` khi repo lỗi; `verify` gọi repo đúng tham số, đúng số lần.
  - Repository impl: `error_code == 0` → `Right` và mapper được áp dụng; `error_code != 0` → `Left(ServerFailure)` đúng message; exception (Dio/parse) → `Left`, không ném ra ngoài.
  - Mapper: JSON đủ field → Entity đúng; field null/thiếu không crash; round-trip nếu có `fromEntity`.
  - Controller GetX: `isLoading` bật/tắt đúng thứ tự; success cập nhật `.obs`; failure gán `errorMessage`, state chính không đổi.
  - Widget: render đúng từ Entity; tương tác chính; trạng thái empty/loading/error.

## Mock & cô lập (§3.1, §3.4)
- [chặn merge] Dùng mocktail, hoặc viết mock tay (`class MockX extends Mock implements X` không qua `@GenerateMocks`), thay vì mockito sinh code.
- [cảnh báo] Sửa tay file `*.mocks.dart`.
- [cảnh báo] Unit test gọi API/Dio thật, Hive/SharedPreferences/secure storage thật không qua mock.
- [cảnh báo] Thêm `mocktail`, `bloc_test`, `freezed`, `json_serializable` vào `dev_dependencies` chỉ để test — CHỈ khi diff có `pubspec.yaml`.

## GetX & viết test (§3.4)
- [chặn merge] File test controller GetX thiếu `Get.testMode = true` trong `setUp` hoặc thiếu `tearDown(Get.reset)`.
- [cảnh báo] Test usecase/entity/mapper (Dart thuần) dùng `testWidgets`/`WidgetTester` không cần thiết.
- [nit] Kiểm `Either` bằng cách ép kiểu/`as` thay vì `fold` hoặc so sánh `Right`/`Left` trực tiếp.
- [nit] File test không mirror đường dẫn `lib/` (ví dụ test của `lib/features/x/data/mappers/y_mapper.dart` không ở `test/features/x/data/mappers/y_mapper_test.dart`).

## Cấu hình CI — CHỈ áp dụng khi diff có workflow CI
- [cảnh báo] Bỏ bước `dart run build_runner build` trước `flutter test`; hạ ngưỡng coverage dưới 70%; không loại `*.g.dart`, `*.freezed.dart`, `*.gen.dart`, `*.mocks.dart` khỏi coverage; bỏ `dart analyze --fatal-infos --fatal-warnings`.
