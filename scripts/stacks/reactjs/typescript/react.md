# Quy tắc React + TypeScript (bổ sung cho `reactjs/react.md`)
Nguồn: Coding Standards — Frontend §2 + CORE §3. CHỈ áp dụng cho file `.ts`/`.tsx`.

- [cảnh báo] Component MỚI dùng `React.FC`/`FunctionComponent` hoặc `defaultProps`; chuẩn là function component với props khai báo bằng `interface XxxProps` và giá trị mặc định qua destructuring. [📐 FE §2.1]
- [cảnh báo] Props/state/response API kiểu `any`, hoặc `useState<any>`; hàm service thiếu kiểu request/response. [📐 FE §11.3; Core §3]
- [cảnh báo] Event handler kiểu `any` thay vì kiểu React (`React.ChangeEvent<HTMLInputElement>`, `React.MouseEvent<...>`). [📐 FE §11.3; Core §3]
- [nit] `useState([])`/`useState(null)` không khai báo generic khi kiểu không suy ra được (`useState<IItem[]>([])`). [📐 Core §3]
- [nit] Ref DOM không khai báo kiểu (`useRef<HTMLDivElement>(null)`). [📐 Core §3]
- [nit] Kiểu `RootState`/`AppDispatch` không dùng khi truy cập store (dùng `useSelector((s: any) => ...)`) — CHỈ khi dự án dùng Redux. [📐 FE §6; Core §3]
