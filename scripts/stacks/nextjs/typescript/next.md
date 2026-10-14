# Quy tắc Next.js + React + TypeScript (bổ sung cho `nextjs/react.md` và `nextjs/next.md`)
Nguồn: Coding Standards — Frontend §2, §5 + CORE §3. CHỈ áp dụng cho file `.ts`/`.tsx`.

- [cảnh báo] Component MỚI dùng `React.FC`/`FunctionComponent` hoặc `defaultProps`; chuẩn là function component với props khai báo bằng `interface XxxProps` và giá trị mặc định qua destructuring.
- [cảnh báo] Props/state/response API kiểu `any`, hoặc `useState<any>`; hàm service thiếu kiểu request/response.
- [cảnh báo] Ép kiểu session/token trong callback auth bằng `as any` ở code MỚI thay vì module augmentation (`declare module 'next-auth' { interface Session { ... } }`).
- [cảnh báo] Event handler kiểu `any` thay vì kiểu React (`React.ChangeEvent<HTMLInputElement>`...).
- [nit] Props của page/layout không khai báo kiểu cho `params`/`searchParams`.
- [nit] `useState([])`/`useState(null)` không khai báo generic khi kiểu không suy ra được; ref DOM không khai báo kiểu.
- [nit] Không dùng kiểu `RootState`/`AppDispatch` khi truy cập store — CHỈ khi dự án dùng Redux.
