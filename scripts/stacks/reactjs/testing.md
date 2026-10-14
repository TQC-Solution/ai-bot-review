# Quy tắc unit test — React/Next.js (Vitest + React Testing Library)
Nguồn: [TECH] Test Standard — Frontend React/Next.js v1.0. Bổ sung cho mục Test trong `core.md`. KHÔNG áp dụng khi luật dự án ghi dự án chưa có test framework.
(Bản sao giống hệt: `reactjs/testing.md` và `nextjs/testing.md`; sửa một chỗ thì đồng bộ chỗ còn lại.)

Bối cảnh chuẩn: Vitest + React Testing Library + `@testing-library/user-event` + jest-dom; mock API ở `services/*` (`vi.mock('@/services/...')`) hoặc network (MSW). File test nằm trong `__tests__/` cạnh source, tên `<tên file source>.test.ts(x)`; fixture/factory ở `src/test/factories/`; setup ở `src/test/setup.ts`. Coverage tối thiểu: statements 70 · branches 65 · functions 70 · lines 70.

## Thiếu test (§3.3, §7.1)
- [cảnh báo] Custom hook có logic, util có nhánh rẽ, RTK slice/reducer, selector có logic MỚI mà PR không có file test tương ứng — CHỈ khi xác minh được danh sách file của PR; không xác minh được thì hỏi.
- [nit] Test có trong diff nhưng thiếu case tối thiểu (CHỈ khi nhìn thấy toàn bộ test của đơn vị đó):
  - Util: happy path; biên (chuỗi rỗng, null/undefined, 0, mảng rỗng); input không hợp lệ.
  - Custom hook: giá trị khởi tạo; state sau hành động; nhánh lỗi (API fail); cleanup khi unmount.
  - RTK slice: initial state; MỖI action một case; payload biên.
  - Selector: state chuẩn; state rỗng/chưa init không crash.
  - Service: resolve đúng shape + gọi đúng endpoint `/v2`; reject chuyển đúng `error_code`.
  - Component: render với props chuẩn; tương tác chính; trạng thái loading/error/empty; không submit khi input invalid.

## Cách test (§3.4)
- [cảnh báo] Test gọi API thật, hoặc mock `axios`/`fetch` trực tiếp trong test component thay vì mock ở ranh giới `services/*` hoặc MSW.
- [cảnh báo] Chờ bất đồng bộ bằng `setTimeout`/sleep thủ công thay vì `findBy*`/`waitFor`.
- [cảnh báo] Test component kiểm state nội bộ, instance, tên class CSS hoặc snapshot toàn bộ DOM làm assertion chính thay vì đầu ra render và phản ứng với tương tác.
- [nit] Query bằng `container.querySelector`, class hoặc `getByTestId` khi có thể dùng `getByRole`/`getByLabelText`/`getByText`.
- [nit] Dùng `fireEvent` cho thao tác người dùng (click, gõ phím) thay vì `userEvent.setup()`.
- [nit] Import trong test bằng đường dẫn tương đối dài thay vì alias `@/`.
- [nit] File test đặt ngoài `__tests__/` của module, hoặc tạo cây thư mục test song song ở gốc dự án.

## Công cụ & cấu hình — CHỈ áp dụng khi diff có `vitest.config.*`, `package.json`, setup test
- [cảnh báo] `vitest.config` đặt `globals: false` hoặc bỏ `globals: true` (RTL không tự cleanup → lỗi "found multiple elements").
- [cảnh báo] Hạ `coverage.thresholds` dưới 70/65/70/70 hoặc xoá thresholds.
- [cảnh báo] `vitest` và `@vitest/coverage-v8` khác major version.
- [nit] Thêm Jest/Enzyme/thư viện test khác cho code mới thay vì bộ chuẩn; CI gọi `vitest` trực tiếp thay vì `npm run test:coverage`.
