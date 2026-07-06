# Hướng dẫn AI Review Pull Request — PubFuture Publisher Tag

Đây là file quy tắc để AI dùng khi review pull request cho repo này. Toàn bộ mã nguồn trong `src/` được bundle thành **`pt.js`** — một thẻ quảng cáo (ad-serving tag) chạy phía trình duyệt, nhúng trực tiếp vào trang của publisher (bên thứ ba, không kiểm soát được). Vì vậy mọi PR phải được đánh giá dưới ba ràng buộc bắt buộc:

1. **Đây là code chạy quảng cáo, chạy trên trang người khác** — tuyệt đối không được làm hỏng trang publisher.
2. **Phải hỗ trợ đa trình duyệt** (Chrome, Safari, Firefox, Edge, các trình duyệt WebView trên mobile).
3. **Phải chạy được trên các version trình duyệt cũ** — target build là **ES2015**.

Khi review, hãy comment cụ thể theo từng mục dưới đây. Ưu tiên chặn (request changes) các lỗi thuộc mục "Chặn merge".

---

## Ngữ cảnh kỹ thuật (Stack)

- **Ngôn ngữ:** JavaScript thuần (ES module trong `src/`, không TypeScript, không framework).
- **Bundler:** esbuild — `format: 'iife'`, `target: 'es2015'`, output `dist/pt.js`; bản phát hành được obfuscate → `dist/pt.min.js` (xem `esbuild.config.mjs`).
- **Runtime:** trình duyệt của publisher. Không có backend trong repo; mọi endpoint được tiêm lúc build qua token `__PF_*__`.
- **Package manager:** pnpm v10, Node 22 (CI).
- **Không có test / lint / typecheck** — reviewer là tuyến phòng thủ chính. Hãy review kỹ tương ứng.
- **Public API duy nhất:** `window.pubfuturetag` (`push`, `divIds`, `consentApi`). Không được tạo thêm biến global nào khác trên `window`.

---

## ⚠️ Tương thích trình duyệt cũ (điểm quan trọng nhất, dễ sai nhất)

esbuild với `target: 'es2015'` **chỉ transpile CÚ PHÁP, KHÔNG polyfill built-in/API runtime.** Đây là nguồn lỗi phổ biến nhất và bắt buộc phải soi kỹ.

### ✅ Được phép (esbuild tự hạ cấp về ES2015)

Các cú pháp này an toàn vì được transpile: arrow function, `async/await`, destructuring, spread/rest, template literal, `class`, `let`/`const`, **optional chaining `?.`**, **nullish coalescing `??`**, default parameter.

### ❌ Chặn merge — built-in/method KHÔNG được polyfill (sẽ crash trên trình duyệt cũ)

Flag ngay nếu PR dùng các API sau mà không có feature-detect + fallback:

- `Promise.allSettled`, `Promise.any` (ES2020/2021) → dùng `Promise.all` + `.catch` từng promise.
- `Array.prototype.flat` / `flatMap` (ES2019) → dùng `reduce`/`concat`.
- `Object.fromEntries` (ES2019), `Object.hasOwn` (ES2022).
- `String.prototype.replaceAll` (ES2021) → dùng `.replace(/.../g, ...)`.
- `Array.prototype.at` (ES2022), `structuredClone`, `globalThis` (ES2020).
- **Regex lookbehind** `(?<=...)` / named group phức tạp — Safari cũ không hỗ trợ và esbuild **không** transpile regex.
- `BigInt` runtime, `WeakRef`, `FinalizationRegistry`.

### ❌ Chặn merge — Web API phải feature-detect trước khi dùng

- `IntersectionObserver`, `ResizeObserver`, `MutationObserver` — **phải** kiểm tra `'IntersectionObserver' in win` và có fallback (repo đã theo pattern này, xem `index.js` và `viewability.js`). Không được giả định luôn tồn tại.
- `fetch` — được inject từ `window.fetch`; không tự gọi `window.fetch` trực tiếp trong module.
- Option `keepalive: true` của fetch không được hỗ trợ ở mọi nơi — với event lúc thoát trang, cân nhắc fallback `navigator.sendBeacon`.
- `URL` constructor, `AudioContext`/`webkitAudioContext`, WebGL context — luôn bọc `try/catch` (fingerprinting modules đã làm vậy).
- `localStorage`/`sessionStorage` — truy cập có thể **throw** (private mode / bị chặn cookie). Phải bọc `try/catch` hoặc dùng helper an toàn trong `pubfutureCommon`.

### CSS render vào trang

- Tránh CSS chỉ có ở trình duyệt mới (`:has()`, container query, `aspect-ratio`...) nếu không có fallback. Dùng đơn vị/thuộc tính có prefix khi cần.

---

## 🛡️ An toàn cho trang publisher (đây là code quảng cáo)

- **Không được throw ra ngoài public API.** Mọi `fetch`, `JSON.parse`, thao tác DOM, truy cập `localStorage` phải nằm trong `try/catch`. Một exception không bắt được có thể làm gãy JS của cả trang publisher → flag ngay.
- **Không làm ô nhiễm global scope.** Không thêm biến/hàm lên `window` ngoài `window.pubfuturetag`. Không sửa prototype của built-in (`Array.prototype`, `String.prototype`...).
- **Rò rỉ bộ nhớ (memory leak) — chặn merge:** mọi `setInterval`/`setTimeout`, `addEventListener`, `IntersectionObserver`/`ResizeObserver`/`MutationObserver` mới thêm **phải** có đường dọn dẹp tương ứng (`clearInterval`/`clearTimeout`, `removeEventListener`, `.disconnect()`). Ad tag sống lâu và refresh nhiều lần → leak tích lũy rất nhanh.
- **Isolation của creative:** giữ nguyên cơ chế render qua iframe/wrapper hiện có; không "phẳng hoá" creative ra trực tiếp DOM trang nếu code cũ dùng iframe.
- **Không block main thread:** không có vòng lặp nặng/đồng bộ dài; ưu tiên async, observer thay vì polling khi có thể.

---

## 📊 Đúng nghiệp vụ quảng cáo

- **Event tracking (`getNewData` / `/v1/adUnits/events`):** giữ nguyên logic queue → flush theo lô (10s) → flush khi `pagehide`, và cơ chế **dedup** (mã `et`: 0=request, 3/4=displayed passback/direct, 5=...). Cẩn thận với lỗi **đếm trùng impression** hoặc thiếu event `et=0`.
- **Passback:** chuỗi dự phòng khi bid không thắng (`tag.passback` → quay lại `push`). Kiểm tra không tạo vòng lặp vô hạn.
- **Parallel configs:** một ad unit phân giải nhiều config cùng lúc dùng **chung một tracking key** (`${tagId}-${rootDivIndex}-parallel`). Thay đổi phải giữ đúng phân biệt parallel vs single kẻo sai số liệu viewability/impression.
- **Refresh & frequency capping:** khi sửa timer refresh, kiểm tra `listTimerRefresh` được clear đúng và `countFrequencyConfig`/`getFrequencyMax` vẫn nhất quán.
- **Viewability:** không phá vỡ điều kiện đo `offsetHeight` và ngưỡng hiển thị hiện có.

---

## 🔧 Quy ước bắt buộc giữ

- **Cấu hình endpoint:** mọi URL dịch vụ dùng token `__PF_*__` (thay lúc build). PR **không** được hardcode URL. Thêm endpoint mới phải kèm: env var + mục `define` trong `esbuild.config.mjs` + cập nhật `.env.example` + các workflow trong `.github/workflows/`.
- **Dependency injection:** module export factory `create*(win, doc, log, fetch, deps, options)`. State dùng chung phải tạo ở `index.js` và truyền vào — không tạo singleton cấp module. Không với tới global thay cho tham số đã inject.
- **Thứ tự khởi tạo** trong `index.js`: fingerprinting → `pubfutureCommon` → support → ad-types. Giữ đúng thứ tự phụ thuộc.
- **Kích thước bundle:** đây là file tải trên mọi trang — cảnh báo nếu PR thêm dependency nặng hoặc phình bundle không cần thiết. Ưu tiên dùng lại helper trong `pubfutureCommon`.
- **Obfuscation:** bản production bị obfuscate → không được dựa vào tên hàm/biến còn sống ở runtime (ví dụ tra cứu qua `Function.name`, so sánh chuỗi tên hàm).

---

## 🚫 KHÔNG flag những thứ sau (tránh nhiễu)

- Các khối code bị comment lớn trong `index.js` (đo timing, `logAdMetricsForUS`) — là instrumentation tắt có chủ đích.
- Comment/commit message bằng tiếng Việt.
- Tên biến rút gọn trong data config (`sz`, `hcp`, `cid`, `ret`, `af`, `iad`, `sad`...) — là hợp đồng dữ liệu với server, không phải code khó đọc.
- Việc thiếu test — repo không có test suite; đừng yêu cầu thêm test trừ khi có hạ tầng test được đưa vào.

---

## Mức độ nghiêm trọng khi review

- **Chặn merge (request changes):** dùng API không polyfill/không feature-detect (mục tương thích); có khả năng throw ra ngoài public API; memory leak (timer/listener/observer không dọn); hardcode endpoint; thêm global lên `window`.
- **Cảnh báo (comment):** phình bundle; lệch pattern DI/thứ tự init; rủi ro đếm trùng event; thiếu fallback cho trình duyệt cũ ở đường phụ.
- **Gợi ý (nit):** đặt tên, dùng lại helper, đơn giản hoá.

Tham chiếu chi tiết từng module: xem `src/README.md` (tiếng Việt) và `CLAUDE.md`.
