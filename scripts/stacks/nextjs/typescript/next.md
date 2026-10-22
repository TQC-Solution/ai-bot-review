# Quy tắc Next.js + React + TypeScript (bổ sung cho `nextjs/react.md` và `nextjs/next.md`)
Nguồn: Coding Standards — Frontend §2, §5 + CORE §3. CHỈ áp dụng cho file `.ts`/`.tsx`.

- [cảnh báo] Component MỚI dùng `React.FC`/`FunctionComponent` hoặc `defaultProps`; chuẩn là function component với props khai báo bằng `interface XxxProps` và giá trị mặc định qua destructuring. [📐 FE §2.1]
- [cảnh báo] Props/state/response API kiểu `any`, hoặc `useState<any>`; hàm service thiếu kiểu request/response. [📐 FE §11.3; Core §3]
- [cảnh báo] Ép kiểu session/token trong callback auth bằng `as any` ở code MỚI thay vì module augmentation (`declare module 'next-auth' { interface Session { ... } }`). [📐 FE §11.3; Core §3]
- [cảnh báo] Event handler kiểu `any` thay vì kiểu React (`React.ChangeEvent<HTMLInputElement>`...). [📐 FE §11.3; Core §3]
- [nit] Props của page/layout không khai báo kiểu cho `params`/`searchParams`. [📐 FE §2.1; Core §3]
- [nit] `useState([])`/`useState(null)` không khai báo generic khi kiểu không suy ra được; ref DOM không khai báo kiểu. [📐 Core §3]
- [nit] Không dùng kiểu `RootState`/`AppDispatch` khi truy cập store — CHỈ khi dự án dùng Redux. [📐 FE §6; Core §3]
