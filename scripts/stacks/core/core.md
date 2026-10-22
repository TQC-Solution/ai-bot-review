# Quy tắc CORE — áp dụng mọi dự án, mọi stack
Nguồn: 📐 Coding Standards — CORE v1.0. Nhãn: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Dòng không có nhãn là mô tả, không dùng để báo lỗi.
Luật riêng của dự án được phép nới hoặc thay thế các quy tắc dưới đây (ví dụ dự án dùng envelope khác, hoặc chưa có test framework).

## Tài liệu căn cứ — dùng để ghi "Căn cứ" khi báo lỗi
Mỗi quy tắc có nhãn đều kết thúc bằng thẻ căn cứ: `[📐 <Mã> §x.y]` = mục trong bản Coding/Test Standard trên Drive; `[📐 ..., suy ra]` = suy ra từ nguyên tắc của mục đó; `[Dự án]` = luật kiến trúc riêng của dự án, không thuộc Code Standard.
| Mã | Tài liệu | Link |
|---|---|---|
| Core | Coding Standards — Core | https://drive.google.com/file/d/1SZXZg2bSFDBy_rdI8n_8DBhfTSz3gWp5/view |
| BE | Coding Standards — Backend Node.js/Express | https://drive.google.com/file/d/1ReQcQiQP3GPuJDCBt0TVcJW8d5OYbpHS/view |
| Go | Coding Standards — Backend Go/Gin | https://drive.google.com/file/d/1Y-Kznirxl3A0yx6ST5WCOSEw1oLuOGym/view |
| FE | Coding Standards — Frontend React/Next.js | https://drive.google.com/file/d/1RczLGrATdNGWnn5FeK8mdMxUDoeOgs62/view |
| Flutter | Coding Standards — Mobile Flutter | https://drive.google.com/file/d/16Q9zvBLVq_cTdMemJMAxI_Nampv7iJ8Z/view |
| SDK | Coding Standards — SDK Mobile | https://drive.google.com/file/d/1EdsfQ4edtVCHDP_6iyo_QoNx6t90MtJ0/view |
| Test Node | Unit Test Standard — Node.js | https://docs.google.com/document/d/1pBiVAGFfihYw-WLcJ59_SgKZKmyVkBu6/edit |
| Test Go | Test Standard — Backend Go/Gin | https://docs.google.com/document/d/1woA8EXpiVRh8DxfTrnwAWA_P-qzl4rXy/edit |
| Test FE | Test Standard — Frontend React/Next.js | https://docs.google.com/document/d/11ZjdbvpL3otawPeVH1zld8ZzxZGC4ZJX/edit |
| Test Flutter | Test Standard — Mobile Flutter | https://docs.google.com/document/d/1Uv7U3vdU82Oca3bCZdA4CbBU3naWqi0H/edit |
"Test Standard §x" (không ghi stack) = mục cùng số trong bản Test Standard của stack đang review (Test Go/FE/Flutter đánh số giống nhau).

Tên mục để ghi kèm số mục:
- Core: §1.2 Nguyên tắc cốt lõi · §1.4 Quy tắc chung · §2 Đặt tên · §3 TypeScript chung · §4.1 Envelope response · §4.2 Mã lỗi · §4.3 Quy ước REST · §5 Bảo mật · §6 Git · §7 Logging · §8 Testing · §9 Tài liệu & vệ sinh repo · §10 Dùng AI.
- BE: §1 Cấu trúc & alias · §2 Kiến trúc phân tầng · §3.1 Route · §3.2 Validator · §3.3 Controller · §4.1 Biz · §4.2 Repo · §4.3 Mapper · §5.1 Response · §5.2 Lỗi · §6.1 Mongoose · §6.2 Sequelize · §7 EventBus · §8 Bull · §9.1 Logging · §9.2 Config/env · §10 Bảo mật · §11 Testing · §12 Style/đặt tên/TS/lint.
- Go: §1 Cấu trúc · §2 Phân tầng · §2.1 Wire · §3.1 Binding · §3.2 Validations · §3.3 Controller · §3.4 Middleware & Router · §4.1 Service · §4.2 Repository · §4.3 Model · §5 Response & lỗi · §6 Xử lý lỗi · §7 Concurrency & context · §8 Hạ tầng · §9 Asynq · §10 Kafka · §11 Logging & cấu hình · §12 Style · §13 Testing · §14 Bảo mật.
- FE: §1 Cấu trúc · §2.1 Component · §2.2 JSX · §3 Style · §4 Hooks & hiệu năng · §5.1 Server/Client · §5.2 NextAuth · §5.3 Metadata/SEO · §6 Redux Toolkit · §7 Gọi API · §8 Bảo mật · §9 Testing · §10 JS thuần · §11 Dùng AI · §12 ESLint/checklist.
- Flutter: §2 Clean Architecture · §3 Domain · §4 Data · §5 Presentation GetX · §6 State/DI/route · §7 Network · §8 Quy ước Dart · §9 Theme/i18n · §10 Xử lý lỗi · §11 Testing · §12 Bảo mật/lưu trữ.
- SDK: §1.1 Public API · §1.2 Ranh giới & đóng gói · §1.3 Threading & lifecycle · §1.4 Lỗi & logging · §1.5 Config/secret/git · §1.6 Tài nguyên & UI · §2 Phụ thuộc module · §3.x Android · §4.x iOS · §5 Wrapper · §6 Luồng CRITICAL · §7 Symbol CRITICAL/HIGH.
- Test Node: §3 Vị trí & tên file · §4 Cấu hình & ngưỡng · §5 AAA · §6 Definition of Done · §7 Mocking (§7.1 DB · §7.2 Redis · §7.3 HTTP · §7.4 Time · §7.5 UUID/random) · §8 Pitfalls.
- Test Go/FE/Flutter: §1.1 Khi nào cần test · §2.2 F.I.R.S.T · §2.3 AAA · §2.4 Đặt tên & phạm vi · §2.5 Test double · §3 Đặc thù stack · §4 Coverage · §5 Quality Gate · §7.1 Case tối thiểu · §7.2 PR checklist.

## Bảo mật
- [chặn merge] Hardcode secret, credential, token, API key, hoặc connection string có mật khẩu trong code mới (file `.env.example` với giá trị giả không tính). [📐 Core §5]
- [chặn merge] Ghép chuỗi truy vấn DB hoặc lệnh hệ thống với dữ liệu từ người dùng; `eval`/`new Function`/thực thi động dữ liệu bên ngoài. [📐 Core §5]
- [chặn merge] Log hoặc trả về client dữ liệu nhạy cảm (mật khẩu, token, số thẻ, PII, ID quảng cáo GAID/IDFA) mà không mask/loại bỏ. [📐 Core §5; Core §7]
- [chặn merge] Lưu mật khẩu thô, hoặc băm bằng MD5/SHA1. [📐 Core §5]
- [chặn merge] Diff xoá bỏ bước validate input, auth hoặc kiểm tra quyền đang có mà không có cơ chế thay thế trong diff. [📐 Core §5]
- [cảnh báo] Endpoint/handler MỚI (hiện đầy đủ trong diff) nhận dữ liệu từ bên ngoài mà không validate. [📐 Core §5]

## Hợp đồng API — áp dụng cho backend trả JSON và client gọi API nội bộ
- Envelope chuẩn: `{ error_code, message, data, pagination? }`; thành công trả HTTP 200 với `error_code = 0`; mã lỗi là số theo dải (1 / 1xx / 4xx / 5xx / 6xx+); field JSON camelCase; thời gian ISO 8601 UTC; prefix `/v2` cho API mới.
- [cảnh báo] Response mới không theo envelope chuẩn (hoặc envelope mà luật dự án quy định). [📐 Core §4.1]
- [cảnh báo] Mã lỗi viết số trần trong logic thay vì hằng số/enum có tên. [📐 Core §4.2]
- [cảnh báo] Client/consumer rẽ nhánh theo nội dung `message` thay vì `error_code`. [📐 Core §4.2]
- [cảnh báo] Đổi shape request/response, tên field hoặc status của endpoint đang dùng mà PR không ghi là breaking change. [📐 Core §4.3]
- [nit] Field JSON mới không camelCase; thời gian không theo ISO 8601 UTC; tiền tệ dùng số thực. [📐 Core §4.3]

## Xử lý lỗi
- [chặn merge] Khối catch mới nuốt lỗi: rỗng, hoặc chỉ return mà không log và không ném/trả lỗi tiếp. [📐 Core §1.2]
- [cảnh báo] Ném/trả lỗi chung chung (chuỗi thô, `Error('error')`) thay vì loại lỗi/mã lỗi của dự án. [📐 Core §1.2; Core §4.2]

## Logging
- [cảnh báo] Dùng `console.log`/`print`/`fmt.Println`/`NSLog` để log trong code production thay vì logger của dự án (script, migration, test không tính). [📐 Core §7]
- [nit] Log lỗi thiếu bối cảnh (id liên quan, thao tác đang làm). [📐 Core §7]

## Cấu hình
- [cảnh báo] Hardcode URL/endpoint/host môi trường production trong code thay vì cấu hình. [📐 BE §9.2; Go §11; FE §7]

## Vệ sinh code
- [cảnh báo] Code mới để lại log gỡ lỗi, `debugger`, khối code bị comment lại, biến/import không dùng. [📐 Core §1.4]
- [nit] Tên không thể hiện ý định (`data2`, `temp`, `obj`), viết tắt tối nghĩa (`usr`, `btn`), boolean không bắt đầu bằng `is/has/should/can`. [📐 Core §2]
- [nit] Hàm mới quá dài, lồng hơn 3 cấp hoặc nhận hơn 3 tham số rời (nên gom thành object/struct). [📐 Core §1.4]
- [nit] Magic number/string lặp lại trong logic mới thay vì hằng số có tên. [📐 Core §1.4]

## Test (chung mọi stack)
Luật chi tiết theo stack nằm trong file `testing.md` của stack (nếu có). KHÔNG áp dụng mục này khi luật dự án ghi dự án chưa có test framework.
Áp dụng cho file test có trong diff (`*.test.*`, `*.spec.*`, `*_test.go`, `*_test.dart`, thư mục `__tests__`/`test/`):
- [chặn merge] Commit test bị "focus": `.only`, `fit`, `fdescribe`, `describe.only`, `test.only`, `solo: true` — các test khác bị bỏ qua, quality gate mất tác dụng. [📐 Core §8; Test Standard §5]
- [cảnh báo] Test MỚI không có assertion nào (chỉ gọi hàm, hoặc chỉ kiểm "không throw" khi hàm có giá trị trả về cần kiểm). (F.I.R.S.T — Self-validating) [📐 Core §8; Test Standard §2.2]
- [cảnh báo] Unit test gọi tài nguyên thật: DB, Redis, Kafka/queue, HTTP/API ngoài, file hệ thống ngoài thư mục fixture. Integration test phải tách riêng (build tag, thư mục/tên riêng). (§2.5) [📐 Core §8; Test Standard §2.5]
- [cảnh báo] Logic test phụ thuộc thời gian thật hoặc ngẫu nhiên (`Date.now()`, `new Date()`, `time.Now()`, `DateTime.now()`, `Math.random`, `uuid`) mà không cố định/mock — test flaky. (F.I.R.S.T — Repeatable) [📐 Core §8; Test Standard §2.2]
- [cảnh báo] Chờ bất đồng bộ bằng sleep/timeout cố định (`setTimeout`, `time.Sleep`, `Future.delayed`) thay vì fake timer/`waitFor`/channel. [📐 Core §8; Test Standard §2.2]
- [cảnh báo] Thêm skip/disable (`.skip`, `xit`, `xdescribe`, `t.Skip`, `skip: true`) mà không ghi lý do + ticket theo dõi trong comment. (Quality Gate) [📐 Core §8; Test Standard §5]
- [cảnh báo] Diff hạ ngưỡng coverage, tắt kiểm tra coverage, hoặc loại thêm file nguồn khỏi coverage mà PR không ghi tech lead đã duyệt. (Quality Gate) [📐 Core §8; Test Standard §5]
- [cảnh báo] Diff xoá test đang có hoặc nới assertion (đổi giá trị mong đợi cho khớp kết quả mới, `toEqual` → `toBeDefined`) mà PR không giải thích thay đổi hành vi — dạng câu hỏi nếu có thể là thay đổi nghiệp vụ hợp lệ. [📐 Core §8; Test Standard §5]
- [cảnh báo] Test phụ thuộc thứ tự/trạng thái của test khác: biến dùng chung bị test trước sửa, không reset mock/state giữa các test. (F.I.R.S.T — Independent) [📐 Core §8; Test Standard §2.2]
- [nit] Test kiểm chi tiết cài đặt thay vì hành vi (state nội bộ, hàm private, số lần gọi hàm nội bộ không thuộc contract). (§1.1) [📐 Core §8; Test Standard §2.4]
- [nit] Tên test không mô tả hành vi theo mẫu [đơn vị] + [điều kiện] + [kết quả mong đợi] (ví dụ `test1`, `should work`); test không chia rõ Arrange – Act – Assert hoặc kiểm nhiều hành vi không liên quan trong một case. (§2.3, §2.4) [📐 Core §8; Test Standard §2.3; Test Standard §2.4]
- [nit] Viết test cho file sinh tự động, getter/setter tầm thường, hằng số. (§2.4) [📐 Core §8; Test Standard §2.4]

Về việc THIẾU test:
- Chỉ xét "thiếu test" khi PR có code MỚI hoặc THAY ĐỔI HÀNH VI: thêm hàm/nhánh/điều kiện, đổi giá trị trả về, ngưỡng, side effect (ghi DB, gửi event, gọi API), hoặc sửa bug.
- KHÔNG báo thiếu test khi PR chỉ: sửa docs/comment/README; đổi format, đổi tên, di chuyển file, tách hàm/refactor KHÔNG đổi hành vi; đổi text log/message hiển thị, style/CSS, layout UI thuần; đổi config/CI/env/`.env.example`, bump dependency; sửa file sinh tự động, migration, script vận hành; xoá code chết.
- KHÔNG báo khi test hiện có đã bao phủ thay đổi: PR sửa/thêm case trong file test của đơn vị đó, hoặc (nếu đọc được repo) file test hiện có đã kiểm đúng nhánh/hành vi vừa đổi. Test cũ gãy vì đổi hành vi sẽ do CI bắt, không cần bot báo.
- Không chắc thay đổi có đổi hành vi hay không: không báo, hoặc hỏi ở mức 💡.
- [cảnh báo] Bug fix (PR/commit mô tả là fix bug) mà PR không có regression test tái hiện bug — CHỈ khi xác minh được danh sách file của PR; không xác minh được thì hỏi. [📐 Core §8; Test Standard §7.1]
- [nit] Đơn vị bắt buộc test theo `testing.md` của stack có THAY ĐỔI HÀNH VI mà PR không thêm/sửa case test nào cho đơn vị đó — dạng câu hỏi. [📐 Core §8; Test Standard §1.1]
