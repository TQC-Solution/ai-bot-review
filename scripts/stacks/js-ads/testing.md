# Quy tắc unit test — JS/TS chạy trên trình duyệt (ad tag, SDK web)
Nguồn: suy ra từ [TECH] Test Standard — Frontend React/Next.js v1.0 (§2 nguyên tắc chung, §4 ngưỡng, §5 Quality Gate, §7 DoD) + nguyên tắc SDK §1, vì công ty chưa có Test Standard riêng cho SDK web. Bổ sung cho mục Test trong `core.md`. Test runner: **Vitest** (môi trường `jsdom`, coverage qua `@vitest/coverage-v8` hoặc `@vitest/coverage-istanbul`) — pubfuture-pt và identity-sdk đều dùng Vitest.
(Bản sao giống hệt: `js-ads/testing.md` và `vanilla-js/testing.md`; sửa một chỗ thì đồng bộ chỗ còn lại.)

Bối cảnh: mỗi module đã có unit test đạt coverage tối thiểu. Code mới/sửa phải giữ mức đó. Ngưỡng tham chiếu khi dự án chưa cấu hình riêng: statements 70 · branches 65 · functions 70 · lines 70. Module viết theo factory nhận phụ thuộc qua tham số (`win`, `doc`, `log`, `fetch`, `deps`, `options` hoặc tương đương) — test truyền object giả vào factory thay vì sửa global.

## Thiếu test
- [cảnh báo] Module/factory MỚI, hàm có nhánh rẽ MỚI (parse config, tính toán frequency/refresh, dedup event, chọn passback, collector, hash/fingerprint, consent) mà PR không có file test tương ứng — CHỈ khi xác minh được danh sách file của PR; không xác minh được thì hỏi. [📐 Test FE §7.1, suy ra]
- Bug fix không kèm regression test: theo luật trong mục Test của `core.md`.
- [nit] Test có trong diff nhưng thiếu case tối thiểu (CHỈ khi nhìn thấy toàn bộ test của đơn vị đó): [📐 Test FE §7.1, suy ra]
  - Hàm thuần: happy path; biên (chuỗi rỗng, null/undefined, 0, mảng rỗng, config thiếu field); input không hợp lệ.
  - Nhánh feature-detect: có API (ví dụ `IntersectionObserver`, `sendBeacon`, `localStorage`) và KHÔNG có API → chạy fallback, không throw.
  - Đường lỗi: `fetch` reject/timeout, `JSON.parse` lỗi, storage throw (private mode) → không ném ra ngoài public API, trả `null`/giá trị mặc định đúng quy ước.
  - Timer/listener/observer: sau destroy/refresh đã được dọn (`clearInterval`, `removeEventListener`, `disconnect` được gọi).
  - Tracking/queue: flush theo lô, flush khi `pagehide`, không gửi trùng (dedup) — với module gửi event.

## Cô lập & mock
- [cảnh báo] Test gửi request mạng thật (endpoint thật, `fetch` không mock); dùng URL production thật trong test thay vì giá trị giả. [📐 Test FE §2.5, suy ra]
- [cảnh báo] Sửa thẳng global (`window.fetch = ...`, `global.localStorage = ...`, `Object.defineProperty(window, ...)`) mà không khôi phục sau test (`vi.stubGlobal` + `vi.unstubAllGlobals()`, `vi.restoreAllMocks()` trong `afterEach`, hoặc `restoreMocks`/`unstubGlobals: true` trong config) — khi module đã hỗ trợ inject phụ thuộc thì ưu tiên truyền object giả vào factory. [📐 Test FE §2.5, suy ra]
- [cảnh báo] Logic dùng `setTimeout`/`setInterval`/`Date.now` (batch flush, refresh, frequency, timeout) mà test chờ thời gian thật thay vì fake timers (`vi.useFakeTimers()` + `vi.advanceTimersByTime(...)`/`vi.setSystemTime(...)`); bật fake timers mà không `vi.useRealTimers()` sau test. [📐 Test FE §2.5, suy ra]
- [cảnh báo] Kết quả phụ thuộc `Math.random`/UUID mà test không cố định giá trị (`vi.spyOn(Math, 'random').mockReturnValue(...)`, mock module tạo UUID). [📐 Test FE §2.2, suy ra]
- [cảnh báo] Test đọc/ghi `localStorage`/`sessionStorage`/cookie của jsdom mà không dọn giữa các test (state rò sang test sau). [📐 Test FE §2.2, suy ra]

## Viết test
- [cảnh báo] Test cho đường "không được throw" chỉ gọi hàm mà không assert giá trị trả về/hành vi fallback (ví dụ chỉ `expect(() => fn()).not.toThrow()` khi hàm có kết quả cần kiểm). [📐 Test FE §2.2, suy ra]
- [cảnh báo] Test phụ thuộc thứ tự khởi tạo module toàn cục (import side-effect của entry gắn lên `window`) mà không reset module giữa các test (`vi.resetModules()` + import động). [📐 Test FE §2.2, suy ra]
- [nit] Test dựa vào tên hàm/biến ở runtime hoặc vào output đã obfuscate/minify thay vì source. [📐 Test FE §2.4, suy ra]
- [nit] Không theo AAA; tên test không mô tả hành vi. [📐 Test FE §2.3, suy ra]

## Cấu hình — CHỈ áp dụng khi diff có `vitest.config.*`/`vite.config.*` (khối `test`), `package.json`, workflow CI
- [cảnh báo] Thêm Jest (`jest`, `ts-jest`, `babel-jest`, `@types/jest`) hoặc viết test mới bằng API `jest.*` thay vì Vitest `vi.*`. [Dự án]
- [cảnh báo] `vitest` và gói coverage (`@vitest/coverage-v8`/`@vitest/coverage-istanbul`) khác major version. [Dự án]
- [cảnh báo] Hạ `test.coverage.thresholds` hoặc xoá thresholds; loại thêm file nguồn khỏi coverage; bỏ bước test khỏi CI. [📐 Test FE §5, suy ra]
- [cảnh báo] Đổi `test.environment` sang `node` cho module dùng DOM, hoặc ngược lại làm test không còn chạy đúng môi trường trình duyệt. [Dự án]
- [nit] Dependency test đặt trong `dependencies` thay vì `devDependencies` (bundle ad tag/SDK không được kéo thư viện test). [Dự án]
