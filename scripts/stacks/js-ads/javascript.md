# Quy tắc JS ad tag — script quảng cáo chạy trên trang publisher
Nguồn: Coding Standards — SDK (§1, suy ra cho SDK web) + CORE. Bối cảnh: bundle bằng esbuild `target: 'es2015'`, `format: 'iife'`, nhúng vào trang bên thứ ba không kiểm soát được. Target build cụ thể theo luật dự án.

## Tương thích trình duyệt cũ — esbuild chỉ transpile CÚ PHÁP, KHÔNG polyfill runtime
- Được phép (esbuild tự hạ cấp): arrow function, `async/await`, destructuring, spread/rest, template literal, `class`, `let`/`const`, `?.`, `??`, default parameter. KHÔNG báo các cú pháp này.
- [chặn merge] Dùng built-in không được polyfill mà không feature-detect + fallback: `Promise.allSettled`/`Promise.any`, `Array.prototype.flat`/`flatMap`/`at`, `Object.fromEntries`/`Object.hasOwn`, `String.prototype.replaceAll`, `structuredClone`, `globalThis`, `BigInt`, `WeakRef`, `FinalizationRegistry`.
- [chặn merge] Regex chỉ có ở trình duyệt mới: lookbehind `(?<=...)`/`(?<!...)`, cờ `s`/`d`, Unicode property escape `\p{...}` — esbuild không transpile regex.
- [chặn merge] Dùng `IntersectionObserver`/`ResizeObserver`/`MutationObserver` không kiểm tra tồn tại (`'IntersectionObserver' in win`) và không có fallback.
- [cảnh báo] `URL` constructor, `AudioContext`/`webkitAudioContext`, WebGL context, `crypto.subtle` không bọc `try/catch`/feature-detect.
- [cảnh báo] Event lúc thoát trang chỉ dùng `fetch({ keepalive: true })` mà không fallback `navigator.sendBeacon`; dùng synchronous XHR.
- [cảnh báo] CSS chèn vào trang dùng tính năng mới (`:has()`, container query, `aspect-ratio`, `inset`) không có fallback.

## An toàn cho trang publisher
- [chặn merge] Code MỚI có thể ném exception ra ngoài public API/entry: `fetch`, `JSON.parse`, thao tác DOM, `localStorage`/`sessionStorage`/cookie (có thể throw ở private mode) không nằm trong `try/catch` — CHỈ khi diff cho thấy đoạn đó không nằm trong khối try của hàm gọi.
- [chặn merge] Thêm biến/hàm lên `window`/`globalThis` ngoài public API duy nhất của dự án; sửa prototype của built-in.
- [chặn merge] `setInterval`/`setTimeout` lặp, `addEventListener`, observer MỚI không có đường dọn dẹp (`clearInterval`/`clearTimeout`, `removeEventListener`, `.disconnect()`) khi ad bị huỷ/refresh.
- [cảnh báo] Vòng lặp nặng/đồng bộ dài trên luồng tải trang; polling khi có thể dùng observer/event.
- [cảnh báo] Render creative thẳng vào DOM trang khi luồng hiện có dùng iframe/wrapper cô lập.

## Quy ước kỹ thuật
- [chặn merge] Hardcode URL/endpoint/secret thay vì build-time constant (token thay lúc build) hoặc config inject.
- [cảnh báo] Module với tới global (`window.fetch`, `document`) thay vì tham số đã inject vào factory `create*(win, doc, log, fetch, deps, options)`; tạo singleton/state cấp module thay vì tạo ở entry và truyền vào.
- [cảnh báo] Dựa vào tên hàm/biến ở runtime (`Function.name`, so sánh chuỗi tên hàm) — bản production bị obfuscate.
- [cảnh báo] `eval`, `new Function`, `setTimeout`/`setInterval` với chuỗi; xử lý `postMessage` không kiểm `event.origin`.
- [cảnh báo] Thêm dependency nặng hoặc code làm phình bundle không cần thiết; không dùng lại helper sẵn có.
- [cảnh báo] `console.*` không đi qua logger có cờ debug; gửi/log raw PII (email, IP, token) thay vì hash/pseudonymize.
