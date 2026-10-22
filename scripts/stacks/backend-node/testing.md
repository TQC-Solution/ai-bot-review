# Quy tắc unit test — Node.js/Express (Jest + supertest)
Nguồn: [TECH] UNIT_TEST_STANDARD — API-level. Bổ sung cho mục Test trong `core.md`. KHÔNG áp dụng khi luật dự án ghi dự án chưa có test framework.
(Bản sao giống hệt: `backend-node/testing.md` và `expressjs/testing.md`; sửa một chỗ thì đồng bộ chỗ còn lại.)

Bối cảnh chuẩn: test API-level đi qua route → middleware (auth) → validation → controller bằng supertest; mock toàn bộ DB, Redis, HTTP client, queue, time, random. File test: `src/api/<module>/__tests__/<module>.<endpoint>.test.(js|ts)` (chấp nhận `__test__`). Jest: `testEnvironment: 'node'`, `restoreMocks: true`, chạy `--runInBand`; ngưỡng coverage global statements 80 · branches 70 · functions 80 · lines 80. Dự án có thể có thêm test tầng biz (gọi thẳng method biz, mock repo) — hợp lệ, không báo sai vị trí.

## Thiếu test (Definition of Done)
- [cảnh báo] Endpoint MỚI (route + controller mới) mà PR không có file test cho endpoint đó — CHỈ khi xác minh được danh sách file của PR; không xác minh được thì hỏi. [📐 Test Node §6]
- [nit] File test cho endpoint mới/sửa thiếu nhóm case bắt buộc: happy path (200), validation (thiếu field, sai kiểu → 400), boundary (null/undefined/chuỗi rỗng/số âm/ngày quá xa), lỗi quyền (401 không token, 403 sai quyền) — CHỈ khi nhìn thấy toàn bộ file test và route có middleware tương ứng (ví dụ không báo thiếu 401/403 cho route public). [📐 Test Node §6]

## Mock
- [cảnh báo] Unit test kết nối DB/Redis/queue thật: `mongoose.connect`, `new Sequelize(...)`/`sequelize.authenticate`, `new Redis(...)`, `createClient()`, Bull `new Queue(...)` trỏ Redis thật, `mongodb-memory-server` trong file unit test API-level. [📐 Test Node §7.1; Test Node §7.2]
- [cảnh báo] Gọi HTTP ngoài thật (axios/fetch tới URL ngoài) trong test thay vì mock HTTP client. [📐 Test Node §7.3]
- [cảnh báo] Mock DB client/driver (ví dụ mock `mongoose.Model.find`, `sequelize.query`) khi dự án có tầng repository — chuẩn yêu cầu mock ở repository/service layer. [📐 Test Node §7.1]
- [cảnh báo] File test dùng `jest.fn()`/`mockResolvedValue` dùng chung giữa các test mà không reset (`afterEach(() => jest.clearAllMocks())`) và config không bật `restoreMocks`/`clearMocks` — CHỈ khi xác minh được config Jest. [📐 Test Node §8; Test Node §4]
- [cảnh báo] Logic phụ thuộc thời gian (`Date.now`, `new Date`, `setTimeout`) mà test không dùng `jest.useFakeTimers()` + `jest.setSystemTime(...)`; bật fake timers mà không `useRealTimers()` ở `afterAll`/`afterEach`. [📐 Test Node §7.4]
- [cảnh báo] Kết quả phụ thuộc `uuid`/`Math.random` mà không `jest.spyOn(...).mockReturnValue(...)`. [📐 Test Node §7.5]
- [nit] Service có cache Redis mà test chỉ có cache hit hoặc chỉ cache miss (chuẩn yêu cầu cả hai). [📐 Test Node §7.2]
- [nit] Service gọi API ngoài mà test chỉ có nhánh success, thiếu failure (`mockRejectedValue`). [📐 Test Node §7.3]

## Viết test
- [cảnh báo] Test API không assert status code, hoặc không assert cấu trúc body (envelope `error_code`/`data`), hoặc không kiểm mock service/repo được gọi đúng tham số khi đó là hành vi chính. [📐 Test Node §5]
- [cảnh báo] `async` test gọi promise mà không `await`/`return` (test pass trước khi assert chạy); `expect(...).rejects` không `await`. [📐 Test Node §8]
- [nit] Không theo cấu trúc AAA (Arrange – Act – Assert). [📐 Test Node §5]
- [nit] File test đặt ngoài `src/api/<module>/__tests__/` hoặc tên không theo `<module>.<endpoint>.test.*`. [📐 Test Node §3]

## Cấu hình — CHỈ áp dụng khi diff có `jest.config.*`, `jest.setup.*` hoặc phần `jest`/`scripts` của `package.json`
- [cảnh báo] Hạ `coverageThreshold` dưới 80/70/80/80 hoặc xoá threshold; thêm file nguồn nghiệp vụ (`src/api`, `src/biz`) vào `coveragePathIgnorePatterns`. [📐 Test Node §4]
- [cảnh báo] Bỏ `--runInBand` khỏi script `test:unit`/`test:coverage`; bỏ `NODE_ENV=test`. [📐 Test Node §4]
- [nit] `testEnvironment` khác `node` cho backend. [📐 Test Node §4]
