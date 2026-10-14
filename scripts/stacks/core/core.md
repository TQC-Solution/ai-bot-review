# Quy tắc CORE — áp dụng mọi dự án, mọi stack
Nguồn: 📐 Coding Standards — CORE v1.0. Nhãn: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Dòng không có nhãn là mô tả, không dùng để báo lỗi.
Luật riêng của dự án được phép nới hoặc thay thế các quy tắc dưới đây (ví dụ dự án dùng envelope khác, hoặc chưa có test framework).

## Bảo mật (Core §5)
- [chặn merge] Hardcode secret, credential, token, API key, hoặc connection string có mật khẩu trong code mới (file `.env.example` với giá trị giả không tính).
- [chặn merge] Ghép chuỗi truy vấn DB hoặc lệnh hệ thống với dữ liệu từ người dùng; `eval`/`new Function`/thực thi động dữ liệu bên ngoài.
- [chặn merge] Log hoặc trả về client dữ liệu nhạy cảm (mật khẩu, token, số thẻ, PII, ID quảng cáo GAID/IDFA) mà không mask/loại bỏ.
- [chặn merge] Lưu mật khẩu thô, hoặc băm bằng MD5/SHA1.
- [chặn merge] Diff xoá bỏ bước validate input, auth hoặc kiểm tra quyền đang có mà không có cơ chế thay thế trong diff.
- [cảnh báo] Endpoint/handler MỚI (hiện đầy đủ trong diff) nhận dữ liệu từ bên ngoài mà không validate.

## Hợp đồng API (Core §4) — áp dụng cho backend trả JSON và client gọi API nội bộ
- Envelope chuẩn: `{ error_code, message, data, pagination? }`; thành công trả HTTP 200 với `error_code = 0`; mã lỗi là số theo dải (1 / 1xx / 4xx / 5xx / 6xx+); field JSON camelCase; thời gian ISO 8601 UTC; prefix `/v2` cho API mới.
- [cảnh báo] Response mới không theo envelope chuẩn (hoặc envelope mà luật dự án quy định).
- [cảnh báo] Mã lỗi viết số trần trong logic thay vì hằng số/enum có tên.
- [cảnh báo] Client/consumer rẽ nhánh theo nội dung `message` thay vì `error_code`.
- [cảnh báo] Đổi shape request/response, tên field hoặc status của endpoint đang dùng mà PR không ghi là breaking change.
- [nit] Field JSON mới không camelCase; thời gian không theo ISO 8601 UTC; tiền tệ dùng số thực.

## Xử lý lỗi (Core §6)
- [chặn merge] Khối catch mới nuốt lỗi: rỗng, hoặc chỉ return mà không log và không ném/trả lỗi tiếp.
- [cảnh báo] Ném/trả lỗi chung chung (chuỗi thô, `Error('error')`) thay vì loại lỗi/mã lỗi của dự án.

## Logging (Core §7)
- [cảnh báo] Dùng `console.log`/`print`/`fmt.Println`/`NSLog` để log trong code production thay vì logger của dự án (script, migration, test không tính).
- [nit] Log lỗi thiếu bối cảnh (id liên quan, thao tác đang làm).

## Cấu hình (Core §5)
- [cảnh báo] Hardcode URL/endpoint/host môi trường production trong code thay vì cấu hình.

## Vệ sinh code (Core §1, §2)
- [cảnh báo] Code mới để lại log gỡ lỗi, `debugger`, khối code bị comment lại, biến/import không dùng.
- [nit] Tên không thể hiện ý định (`data2`, `temp`, `obj`), viết tắt tối nghĩa (`usr`, `btn`), boolean không bắt đầu bằng `is/has/should/can`.
- [nit] Hàm mới quá dài, lồng hơn 3 cấp hoặc nhận hơn 3 tham số rời (nên gom thành object/struct).
- [nit] Magic number/string lặp lại trong logic mới thay vì hằng số có tên.

## Test (Core §8 + Test Standard §2, §5 — chung mọi stack)
Luật chi tiết theo stack nằm trong file `testing.md` của stack (nếu có). KHÔNG áp dụng mục này khi luật dự án ghi dự án chưa có test framework.
Áp dụng cho file test có trong diff (`*.test.*`, `*.spec.*`, `*_test.go`, `*_test.dart`, thư mục `__tests__`/`test/`):
- [chặn merge] Commit test bị "focus": `.only`, `fit`, `fdescribe`, `describe.only`, `test.only`, `solo: true` — các test khác bị bỏ qua, quality gate mất tác dụng.
- [cảnh báo] Test MỚI không có assertion nào (chỉ gọi hàm, hoặc chỉ kiểm "không throw" khi hàm có giá trị trả về cần kiểm). (F.I.R.S.T — Self-validating)
- [cảnh báo] Unit test gọi tài nguyên thật: DB, Redis, Kafka/queue, HTTP/API ngoài, file hệ thống ngoài thư mục fixture. Integration test phải tách riêng (build tag, thư mục/tên riêng). (§2.5)
- [cảnh báo] Logic test phụ thuộc thời gian thật hoặc ngẫu nhiên (`Date.now()`, `new Date()`, `time.Now()`, `DateTime.now()`, `Math.random`, `uuid`) mà không cố định/mock — test flaky. (F.I.R.S.T — Repeatable)
- [cảnh báo] Chờ bất đồng bộ bằng sleep/timeout cố định (`setTimeout`, `time.Sleep`, `Future.delayed`) thay vì fake timer/`waitFor`/channel.
- [cảnh báo] Thêm skip/disable (`.skip`, `xit`, `xdescribe`, `t.Skip`, `skip: true`) mà không ghi lý do + ticket theo dõi trong comment. (Quality Gate)
- [cảnh báo] Diff hạ ngưỡng coverage, tắt kiểm tra coverage, hoặc loại thêm file nguồn khỏi coverage mà PR không ghi tech lead đã duyệt. (Quality Gate)
- [cảnh báo] Diff xoá test đang có hoặc nới assertion (đổi giá trị mong đợi cho khớp kết quả mới, `toEqual` → `toBeDefined`) mà PR không giải thích thay đổi hành vi — dạng câu hỏi nếu có thể là thay đổi nghiệp vụ hợp lệ.
- [cảnh báo] Test phụ thuộc thứ tự/trạng thái của test khác: biến dùng chung bị test trước sửa, không reset mock/state giữa các test. (F.I.R.S.T — Independent)
- [nit] Test kiểm chi tiết cài đặt thay vì hành vi (state nội bộ, hàm private, số lần gọi hàm nội bộ không thuộc contract). (§1.1)
- [nit] Tên test không mô tả hành vi theo mẫu [đơn vị] + [điều kiện] + [kết quả mong đợi] (ví dụ `test1`, `should work`); test không chia rõ Arrange – Act – Assert hoặc kiểm nhiều hành vi không liên quan trong một case. (§2.3, §2.4)
- [nit] Viết test cho file sinh tự động, getter/setter tầm thường, hằng số. (§2.4)

Về việc THIẾU test:
- Chỉ xét "thiếu test" khi PR có code MỚI hoặc THAY ĐỔI HÀNH VI: thêm hàm/nhánh/điều kiện, đổi giá trị trả về, ngưỡng, side effect (ghi DB, gửi event, gọi API), hoặc sửa bug.
- KHÔNG báo thiếu test khi PR chỉ: sửa docs/comment/README; đổi format, đổi tên, di chuyển file, tách hàm/refactor KHÔNG đổi hành vi; đổi text log/message hiển thị, style/CSS, layout UI thuần; đổi config/CI/env/`.env.example`, bump dependency; sửa file sinh tự động, migration, script vận hành; xoá code chết.
- KHÔNG báo khi test hiện có đã bao phủ thay đổi: PR sửa/thêm case trong file test của đơn vị đó, hoặc (nếu đọc được repo) file test hiện có đã kiểm đúng nhánh/hành vi vừa đổi. Test cũ gãy vì đổi hành vi sẽ do CI bắt, không cần bot báo.
- Không chắc thay đổi có đổi hành vi hay không: không báo, hoặc hỏi ở mức 💡.
- [cảnh báo] Bug fix (PR/commit mô tả là fix bug) mà PR không có regression test tái hiện bug — CHỈ khi xác minh được danh sách file của PR; không xác minh được thì hỏi.
- [nit] Đơn vị bắt buộc test theo `testing.md` của stack có THAY ĐỔI HÀNH VI mà PR không thêm/sửa case test nào cho đơn vị đó — dạng câu hỏi.
