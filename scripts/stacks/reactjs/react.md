# Quy tắc React — chung cho các frontend React/Next.js (JS và TS)
Nguồn: Coding Standards — Frontend React/Next.js v1.0 §2–§8 + CORE. Thư viện cụ thể (AntD, RTK, axios instance, thư mục `services/`) theo luật dự án; khi dự án dùng lựa chọn khác nhưng nhất quán, theo luật dự án.
(Bản sao giống hệt: `reactjs/react.md` và `nextjs/react.md`; sửa một chỗ thì đồng bộ chỗ còn lại.)

## Component & hooks (FE §2, §4)
- [chặn merge] Vi phạm Rules of Hooks: gọi hook trong điều kiện, vòng lặp, sau `return` sớm, hoặc trong hàm không phải component/custom hook.
- [chặn merge] `useEffect` MỚI tạo subscription/timer/listener (`setInterval`, `addEventListener`, socket) mà không trả hàm cleanup.
- [cảnh báo] Thiếu dependency trong `useEffect`/`useMemo`/`useCallback` khi biến dùng bên trong rõ ràng thay đổi theo render (props/state) — không báo với setter của `useState`, ref, hằng ngoài component.
- [cảnh báo] `setState` trực tiếp trong thân render, hoặc trong `useEffect` không điều kiện gây render vô hạn.
- [cảnh báo] Mutate state/props trực tiếp (`state.items.push(...)` rồi `setState(state)`) ngoài Immer/RTK reducer.
- [cảnh báo] Class component MỚI.
- [cảnh báo] `key={index}` cho danh sách có thể đổi thứ tự/thêm/xoá; thiếu `key` khi render danh sách.
- [nit] Dùng `useEffect` + state để tính dữ liệu dẫn xuất từ props/state (nên tính trực tiếp hoặc `useMemo`).
- [nit] Component MỚI quá lớn (> ~150 dòng hoặc nhiều trách nhiệm); logic phức tạp nên tách custom hook.
- [nit] Rải `memo`/`useMemo`/`useCallback` không có lý do hiệu năng.

## Bảo mật & dữ liệu (FE §8)
- [chặn merge] `dangerouslySetInnerHTML` với dữ liệu chưa sanitize; gán `href`/`src` từ dữ liệu người dùng mà không chặn `javascript:`.
- [chặn merge] Secret/API key bí mật trong code client hoặc biến môi trường public (`REACT_APP_*`, `VITE_*`, `NEXT_PUBLIC_*`).
- [cảnh báo] Lưu token vào `localStorage` khi dự án đã có cơ chế lưu khác (cookie httpOnly, NextAuth).
- [cảnh báo] Chỉ ẩn UI để phân quyền mà không có kiểm tra phía server/route guard — dạng câu hỏi.

## API & state (FE §6, §7)
- [cảnh báo] Component/hook gọi `axios`/`fetch` trực tiếp thay vì hàm trong tầng service của dự án; tạo axios instance mới ngoài file cấu hình HTTP client.
- [cảnh báo] Đọc `process.env`/`import.meta.env` rải rác thay vì module cấu hình env tập trung.
- [cảnh báo] Xử lý lỗi API dựa vào nội dung `message` thay vì `error_code`.
- [cảnh báo] Redux viết tay (`createStore`, action type/creator thủ công) thay vì Redux Toolkit; đọc `state.x.y` lặp lại thay vì selector — CHỈ khi dự án dùng Redux.
- [cảnh báo] Dữ liệu không serializable (class instance, function, `Date` thô) đưa vào Redux store.
- [nit] Đưa state chỉ dùng cục bộ vào store toàn cục.

## Style & UI (FE §3)
- [cảnh báo] `style={{...}}` cho style tĩnh; hardcode màu/khoảng cách/breakpoint thay vì biến SCSS/token/class Tailwind của dự án. Style động theo dữ liệu (ví dụ `width` tính toán) được phép.
- [nit] Tự dựng lại component khi thư viện UI dự án dùng (AntD...) đã có sẵn; nối class bằng tay thay vì `clsx`/`classnames` khi dự án đã dùng.

## Accessibility & HTML (FE §4)
- [cảnh báo] `<img>` thiếu `alt`; phần tử không phải button/link có `onClick` mà không có `role` và xử lý bàn phím.
- [nit] `<button>` trong form thiếu `type`; dùng `<div>` thay thẻ ngữ nghĩa.

## Test (FE §9)
- [nit] Custom hook/util có logic nhánh MỚI hoặc bug fix không có test — dạng câu hỏi; không áp dụng nếu luật dự án ghi chưa có test.
