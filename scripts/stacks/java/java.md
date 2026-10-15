# Quy tắc Java — chỉ CORE
Nguồn: Coding Standards — CORE v1.0 + checklist AI review `REVIEW.java.md` (mục B). Chưa có bản Coding Standards riêng cho Java: review theo `core/core.md`, bổ sung các mục dưới đây. Nhãn: [chặn merge] = MUST · [cảnh báo] = SHOULD · [nit] = NOTE.

- KHÔNG áp pattern của Node.js/Go vào repo Java (Core §10.1); bám cấu trúc, cách đặt tên và pattern đang có trong repo.
- Quy ước tên của Core: biến/hàm camelCase, class PascalCase, hằng số UPPER_SNAKE.

## Consumer / stream
- [chặn merge] Xử lý message MỚI không idempotent nhìn thấy được (ghi/cộng dồn dữ liệu mà không kiểm tra đã xử lý chưa).
- [chặn merge] Commit offset trước khi xử lý message xong.
- [chặn merge] Consumer/thread MỚI không dừng được khi shutdown (không có shutdown hook, vòng lặp poll không kiểm tra cờ dừng).

## Log & cấu hình
- [chặn merge] `System.out.println`/`System.err.println`/`printStackTrace()` để log thay vì logger của repo; log token/PII.
- [chặn merge] Cấu hình/secret hardcode thay vì đọc từ biến môi trường hoặc file cấu hình không commit.
- [cảnh báo] Tên biến/hàm/class MỚI lệch quy ước camelCase/PascalCase/UPPER_SNAKE.
