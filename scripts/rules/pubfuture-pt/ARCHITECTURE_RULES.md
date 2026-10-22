# PubFuture Publisher Tag (`pt.js`) — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của repo PubFuture Publisher Tag. Căn cứ: 📐 Coding Standards — CORE + nguyên tắc SDK §1 (áp dụng cho script chạy trên trang đối tác).
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.

## 1. Tổng quan
Mã nguồn `src/` được bundle thành **`pt.js`** — thẻ quảng cáo chạy phía trình duyệt, nhúng vào trang publisher (bên thứ ba). Ba ràng buộc bắt buộc:
1. Code quảng cáo chạy trên trang người khác: tuyệt đối không làm hỏng trang publisher.
2. Đa trình duyệt: Chrome, Safari, Firefox, Edge, WebView mobile.
3. Trình duyệt cũ: target build **ES2015**.

Stack: JavaScript thuần (ES module, không TypeScript, không framework). esbuild `format: 'iife'`, `target: 'es2015'` → `dist/pt.js`; bản phát hành obfuscate → `dist/pt.min.js` (`esbuild.config.mjs`). Endpoint tiêm lúc build qua token `__PF_*__`. pnpm v10, Node 22 (CI). Đã có unit test (backfill đạt coverage tối thiểu); chưa có lint/typecheck — review vẫn là tuyến phòng thủ chính cho tương thích trình duyệt.
Public API duy nhất: `window.pubfuturetag` (`push`, `divIds`, `consentApi`).

## 2. Cấu trúc & quy ước
- Module export factory `create*(win, doc, log, fetch, deps, options)`; state dùng chung tạo ở `index.js` rồi truyền vào.
- Thứ tự khởi tạo trong `index.js`: fingerprinting → `pubfutureCommon` → support → ad-types.
- `pubfutureCommon`: helper dùng chung (kể cả truy cập storage an toàn).
- Event tracking (`getNewData` → `/v1/adUnits/events`): queue → flush theo lô 10s → flush khi `pagehide`; dedup theo mã `et` (0 = request, 3/4 = displayed passback/direct, 5 = ...).
- Passback: `tag.passback` → quay lại `push`.
- Parallel configs: một ad unit phân giải nhiều config cùng lúc, dùng chung tracking key `${tagId}-${rootDivIndex}-parallel`.
- Refresh/frequency: `listTimerRefresh`, `countFrequencyConfig`, `getFrequencyMax`. Viewability dựa trên `offsetHeight` và ngưỡng hiển thị hiện có.
- Chi tiết module: `src/README.md`, `CLAUDE.md`.

## 3. Luật review
(Các luật tương thích ES2015, feature-detect và an toàn trang host chung nằm ở stack `js-ads`; mục dưới đây là phần riêng hoặc nhấn mạnh của repo.)

### 3.1. Tương thích & an toàn trang publisher
- [chặn merge] Built-in không polyfill / regex mới / Web API không feature-detect (theo danh sách trong stack `js-ads`). [Dự án]
- [chặn merge] Code mới có thể ném exception ra ngoài `window.pubfuturetag` (fetch, `JSON.parse`, DOM, storage không trong try/catch). [📐 SDK §1.4, suy ra]
- [chặn merge] Thêm biến/hàm global ngoài `window.pubfuturetag`; sửa prototype built-in. [📐 SDK §1.2, suy ra]
- [chặn merge] Timer/listener/observer mới không có đường dọn (`clearInterval`/`clearTimeout`, `removeEventListener`, `.disconnect()`). [📐 SDK §1.3, suy ra]
- [chặn merge] Truy cập `localStorage`/`sessionStorage` trực tiếp không try/catch và không qua helper của `pubfutureCommon`. [📐 SDK §1.4, suy ra]
- [cảnh báo] Render creative thẳng vào DOM trang khi luồng cũ dùng iframe/wrapper. [Dự án]
- [cảnh báo] Fallback cho trình duyệt cũ thiếu ở đường phụ (không phải luồng chính). [Dự án]

### 3.2. Nghiệp vụ quảng cáo
- [chặn merge] Thay đổi làm đếm trùng impression hoặc mất event `et=0`; phá cơ chế dedup hoặc flush khi `pagehide`. [Dự án]
- [chặn merge] Passback có thể tạo vòng lặp vô hạn (không có điều kiện dừng). [Dự án]
- [cảnh báo] Trộn lẫn tracking key parallel và single (`${tagId}-${rootDivIndex}-parallel`). [Dự án]
- [cảnh báo] Sửa timer refresh mà `listTimerRefresh` không được clear đúng, hoặc `countFrequencyConfig`/`getFrequencyMax` không còn nhất quán. [Dự án]
- [cảnh báo] Đổi điều kiện đo viewability (`offsetHeight`, ngưỡng). [Dự án]

### 3.3. Quy ước bắt buộc giữ
- [chặn merge] Hardcode URL dịch vụ thay vì token `__PF_*__`. [📐 SDK §1.5, suy ra; Core §5]
- [cảnh báo] Endpoint mới có token nhưng thiếu một trong các bước: env var, mục `define` trong `esbuild.config.mjs`, `.env.example`, workflow trong `.github/workflows/` — CHỈ báo phần xác minh được là thiếu. [Dự án]
- [cảnh báo] Module với tới global thay vì tham số đã inject; tạo singleton cấp module. [Dự án]
- [cảnh báo] Đổi thứ tự khởi tạo trong `index.js` trái chiều phụ thuộc. [Dự án]
- [cảnh báo] Dựa vào `Function.name` hoặc so sánh chuỗi tên hàm (bị obfuscate). [Dự án]
- [cảnh báo] Thêm dependency nặng hoặc phình bundle; không dùng lại helper của `pubfutureCommon`. [📐 Core §1.2]
- [nit] Đặt tên, đơn giản hoá, dùng lại helper. [📐 Core §2; Core §1.2]

### 3.4. Test
Repo đã backfill unit test đạt coverage tối thiểu theo Test Standard: luật trong mục Test của `core.md` và `testing.md` của stack áp dụng đầy đủ cho code MỚI và thay đổi HÀNH VI. PR không đổi hành vi (refactor, đổi tên, docs, config, UI thuần...) không bị yêu cầu test.
- [cảnh báo] Thay đổi logic tracking (queue, flush 10s, flush `pagehide`, dedup theo `et`), passback, parallel key, refresh/frequency mà PR không có test cho hành vi đó — CHỈ khi thay đổi đổi hành vi (thêm/sửa nhánh, điều kiện, ngưỡng, kết quả) VÀ PR không thêm/sửa case test nào cho phần đó VÀ (nếu đọc được repo) test hiện có chưa kiểm hành vi mới; refactor không đổi hành vi thì KHÔNG báo. [📐 Test FE §7.1, suy ra]
- [nit] Test module mới không tạo qua factory `create*(win, doc, log, fetch, deps, options)` với phụ thuộc giả mà sửa global. [📐 Test FE §2.5, suy ra]

## 4. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo
- Khối code bị comment lớn trong `index.js` (đo timing, `logAdMetricsForUS`): instrumentation tắt có chủ đích.
- Comment/commit message tiếng Việt.
- Tên rút gọn trong data config (`sz`, `hcp`, `cid`, `ret`, `af`, `iad`, `sad`...): hợp đồng dữ liệu với server.
- Thiếu TypeScript, thiếu lint: KHÔNG yêu cầu thêm.

## 5. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Theo pattern DI và thứ tự init hiện có; dùng helper `pubfutureCommon`; mọi endpoint mới đi qua token `__PF_*__`.
