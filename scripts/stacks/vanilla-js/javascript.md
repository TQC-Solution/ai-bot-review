# Quy tắc JavaScript/TypeScript trên trình duyệt — SDK/script nhúng vào trang khác
Nguồn: Coding Standards — SDK (§1, suy ra cho SDK web) + CORE. Target trình duyệt và build chain theo luật dự án.

## Public API
- [chặn merge] Đổi/xoá tên hoặc signature của Public API (object global, hàm export, option khởi tạo, callback/event) mà PR không ghi là breaking change (major version + changelog). [📐 SDK §1.1, suy ra]
- [chặn merge] Gán thêm biến lên `window`/`globalThis` ngoài namespace public duy nhất của SDK. [📐 SDK §1.2, suy ra]
- [cảnh báo] Public API ném exception ra trang host khi không phải dùng sai rõ ràng. [📐 SDK §1.4, suy ra]

## Fail-safe & hiệu năng trang host
- [chặn merge] Browser API có thể không tồn tại (`navigator.*`, `crypto`, `IntersectionObserver`, `indexedDB`, WebGL, Audio) dùng mà không feature-detect — CHỈ khi diff cho thấy rõ không có kiểm tra ở hàm gọi. [📐 SDK §1.4, suy ra]
- [chặn merge] Thao tác có thể throw (`localStorage`, `sessionStorage`, `IndexedDB`, cookie, `JSON.parse`) không bọc `try/catch` — exception không được thoát ra trang host. [📐 SDK §1.4, suy ra]
- [chặn merge] Synchronous XHR; vòng lặp nặng/tác vụ dài `await` trực tiếp trên critical path tải trang. [📐 SDK §1.3, suy ra]
- [cảnh báo] Timer/listener/observer MỚI không có đường dọn dẹp; có khả năng gọi callback 2 lần. [📐 SDK §1.3, suy ra]
- [cảnh báo] Request lúc thoát trang không dùng `sendBeacon` (hoặc fallback tương đương). [Dự án]

## Bảo mật & dữ liệu
- [chặn merge] Gửi/log raw PII (email, IP, token) thay vì hash/pseudonymize; lưu token/PII thô vào storage của trình duyệt. [📐 Core §5; Core §7]
- [chặn merge] Hardcode endpoint/secret thay vì build-time constant hoặc config khởi tạo. [📐 Core §5; SDK §1.5, suy ra]
- [cảnh báo] `eval`, `new Function`; xử lý `postMessage` không kiểm `event.origin`; dùng dữ liệu từ DOM/query string mà không validate. [📐 Core §5]
- [cảnh báo] `console.*` không đi qua logger có cờ debug. [📐 Core §7]

## Quy ước
- [nit] Trả `undefined` cho "không có dữ liệu" khi quy ước dự án là `null`. [Dự án]
- [nit] Thêm dependency runtime làm tăng bundle khi có thể tự viết ngắn gọn hoặc đã có helper. [📐 Core §1.2]
