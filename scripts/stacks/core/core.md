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

## Test (Core §8)
- [nit] Bug fix hoặc logic nghiệp vụ mới mà PR không có test: chỉ nêu dưới dạng câu hỏi ("Đã có test cho trường hợp này chưa?"). KHÔNG áp dụng khi luật dự án ghi dự án chưa có test framework.
