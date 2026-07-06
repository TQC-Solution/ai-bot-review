# Review Prompt Templates

Thư mục này chứa các **prompt template** dùng chung cho AI review. Đây là phần "thân" prompt — trung lập với ngôn ngữ/framework; kiến thức đặc thù công nghệ được nạp động qua biến `{coding_stack}` và `{coding_rules}`.

## Files

- **`review_prompt_vi.txt`** — template tiếng Việt (mặc định)
- **`review_prompt_en.txt`** — template tiếng Anh

> ⚠️ Hai file này phải **đồng bộ về mặt logic**. Khi sửa tiêu chí/format ở một file, hãy áp dụng thay đổi tương ứng cho file còn lại — nếu không, kết quả review sẽ khác nhau tùy `review-language`.

## Prompt được lắp ráp như thế nào

`ai_review.py` → `PromptBuilder` thực hiện:

1. Đọc env `STACK` và `RULES_PATH` (truyền từ `action.yml` / workflow).
2. Ghép **tất cả** file `.md` trong `scripts/stacks/<STACK>/` → `{coding_stack}`.
3. Ghép **tất cả** file `.md` trong `scripts/rules/<RULES_PATH>/` → `{coding_rules}`.
4. Chọn template theo `REVIEW_LANGUAGE`, thay các placeholder.
5. **Diff lớn được chia nhỏ**: `DiffChunker` cắt theo ranh giới file, mỗi chunk ~40.000 ký tự, và review **từng chunk độc lập**. Vì vậy prompt phải luôn giả định model *chỉ thấy một phần diff* — tuyệt đối không phán "file không tồn tại" chỉ vì nó không nằm trong phần đang xem.

## Template Variables

| Placeholder      | Nguồn dữ liệu                                   | Vị trí trong template VI                     |
| ---------------- | ----------------------------------------------- | -------------------------------------------- |
| `{coding_stack}` | Các `.md` trong `scripts/stacks/<STACK>/`       | dưới `=== QUY TẮC & CHUẨN MỰC LẬP TRÌNH ===` |
| `{coding_rules}` | Các `.md` trong `scripts/rules/<RULES_PATH>/`   | dưới `=== KIẾN TRÚC & LUẬT TRONG DỰ ÁN ===`  |
| `{code_diff}`    | Diff (hoặc một chunk) của pull request           | dưới `=== CODE DIFF CẦN REVIEW ===`          |

- `{coding_stack}` = persona + tiêu chí ở tầng **công nghệ/stack** (vd `expressjs`, `nextjs/typescript`, `js-ads`).
- `{coding_rules}` = quy tắc **kiến trúc đặc thù dự án** (vd `pubfuture-pt`, `pubstar-ios`).
- Hai nguồn này **bổ sung** cho nhau: stack = "viết đúng ngôn ngữ", rules = "viết đúng dự án".

## Cấu trúc template

```
[Định nghĩa vai trò — senior software engineer]

=== QUY TẮC & CHUẨN MỰC LẬP TRÌNH ===
{coding_stack}

=== KIẾN TRÚC & LUẬT TRONG DỰ ÁN ===
{coding_rules}

=== NHIỆM VỤ CỦA BẠN ===
[Các nhóm tiêu chí review — trung lập với stack]

[Yêu cầu về format & mức độ nghiêm trọng]

[Ví dụ format với emoji — dùng placeholder chung, không gắn ngôn ngữ cụ thể]

=== CODE DIFF CẦN REVIEW ===
{code_diff}
```

## Viết prompt sao cho AI review TỐT hơn

Đây là phần quan trọng nhất. Mục tiêu: **đúng, ít nhiễu, và hành động được**. Khi chỉnh template, giữ các nguyên tắc sau:

**1. Ưu tiên độ chính xác hơn số lượng (giảm false-positive).**
- Yêu cầu model chỉ báo lỗi khi **quan sát được trực tiếp trong diff**, không suy đoán. Với nghi ngờ chưa chắc, hạ xuống mức 💡 gợi ý thay vì 🔴.
- Nêu rõ mã cũ không nằm trong diff có thể chứa ngữ cảnh cần thiết → không được kết luận thiếu sót chỉ vì không thấy.

**2. Bám vào diff, tôn trọng chunk.**
- Nhắc lại (đã có, cần giữ): "CHỈ review code trong diff", "KHÔNG nói file không tồn tại".
- Vì review theo chunk, tránh yêu cầu model thống kê/tổng hợp toàn PR trong một lần.

**3. Phân mức nghiêm trọng nhất quán.**
- 🔴 Critical = bug chắc chắn, lỗ hổng bảo mật, vi phạm kiến trúc cứng, có thể gây hỏng runtime.
- ⚠️ Warning = rủi ro thật nhưng không chắc chắn hỏng / lệch quy ước quan trọng.
- 💡 Suggestion = chất lượng, đặt tên, tái sử dụng.
- Ép **liệt kê theo thứ tự 🔴 → ⚠️ → 💡** và **gom nhóm cùng loại lỗi** để dễ đọc.

**4. Actionable.** Mỗi phát hiện phải có: `file:line`, mô tả ngắn *vì sao sai*, và `→ Fix/Suggestion` cụ thể (kèm ví dụ code khi hữu ích).

**5. Định hướng bằng dữ liệu nạp động, không hardcode vào thân prompt.**
- Muốn AI bắt lỗi đặc thù công nghệ mới → thêm/sửa file trong `scripts/stacks/` hoặc `scripts/rules/`, **đừng** nhồi vào template (template dùng chung mọi dự án).
- Trong file stack/rules, đánh dấu rõ mức độ (vd "**Chặn merge**", "**Cảnh báo**", "nit") để model ánh xạ đúng sang emoji.

**6. Chống nhiễu.** Cho phép model kết luận sạch: nếu không có lỗi, trả đúng câu "✅ ..." thay vì bịa vấn đề để có gì đó báo cáo.

**7. Ngôn ngữ đầu ra.** Ràng buộc trả lời hoàn toàn bằng đúng một ngôn ngữ (VI hoặc EN) khớp với template đang dùng.

## Cách tùy chỉnh

1. **Sửa template có sẵn**: chỉnh trực tiếp file `.txt` — nhớ đồng bộ cả VI và EN.
2. **Thêm ngôn ngữ mới**: tạo `review_prompt_ja.txt` và cập nhật `ai_review.py`:

```python
def load_prompt_template(language: str) -> str:
    if language == "english":
        prompt_file = "review_prompt_en.txt"
    elif language == "japanese":
        prompt_file = "review_prompt_ja.txt"
    else:  # Vietnamese (default)
        prompt_file = "review_prompt_vi.txt"
    ...
```

> Lưu ý: template được thiết kế dùng chung cho MỌI stack/rule. Sửa thân prompt ảnh hưởng **tất cả** dự án đang dùng bot — hãy giữ nó trung lập, chỉ chứa tiêu chí và format.

## Lợi ích của cách tách template

- ✅ **Dễ đọc**: text thuần, không phải escape chuỗi Python.
- ✅ **Dễ sửa**: không cần đụng code Python để đổi prompt.
- ✅ **Version control**: theo dõi thay đổi prompt tách biệt với logic.
- ✅ **Cộng tác**: người không phải dev cũng cập nhật được.
- ✅ **Thử nghiệm**: dễ so sánh các phiên bản prompt khác nhau.
