# Review Prompt Templates

Thư mục này chứa **prompt template** dùng chung cho AI review và script lắp ráp prompt. Template trung lập với ngôn ngữ/framework; kiến thức đặc thù được nạp động qua `{coding_stack}` và `{coding_rules}`.

## Files

- **`review_prompt_vi.txt`** — template tiếng Việt (mặc định)
- **`review_prompt_en.txt`** — template tiếng Anh (luật nạp vào vẫn bằng tiếng Việt; template EN có phần giải nghĩa nhãn)
- **`build-prompt.sh`** — lắp prompt cho luồng chính (`action.yml` → `anthropics/claude-code-action`)

> ⚠️ Hai template phải **đồng bộ về logic**. Sửa tiêu chí/format ở một file thì sửa tương ứng file còn lại.
> ⚠️ Template KHÔNG được chứa ký tự `{` `}` ngoài 3 placeholder (luồng Python cũ dùng `str.format`). Nội dung luật được truyền làm giá trị nên chứa ngoặc nhọn thoải mái.

## Prompt được lắp ráp như thế nào

### Luồng chính — `build-prompt.sh` (Claude Code action)

1. Đọc env `STACK`, `RULES_PATH`, `REVIEW_LANGUAGE` từ `action.yml`.
2. `{coding_stack}` = `stacks/core/*.md` → file `.md` trực tiếp trong các thư mục cha của `STACK` (stack lồng nhau như `nextjs/typescript`) → file `.md` trực tiếp trong `stacks/<STACK>/`.
3. `{coding_rules}` = mọi file `.md` trong `rules/<RULES_PATH>/` (đệ quy).
4. `{code_diff}` = câu hướng dẫn Claude tự lấy diff bằng `gh pr diff`; Claude có thể đọc file liên quan trong repo để xác minh trước khi báo lỗi.
5. Thay placeholder bằng `str.replace` (python3), rồi nối thêm mục "Review Requirements" (inline comment + 1 comment tổng kết, không sửa code).

### Luồng cũ — `scripts/reviewer/prompt_builder.py` (đang tạm dừng, `REVIEW_PAUSED = True`)

Nạp stack/rules theo cùng thứ tự, thay placeholder bằng `str.format`, nhúng diff thật. Diff lớn được `DiffChunker` cắt theo file (~40.000 ký tự/chunk) và review **từng chunk độc lập** — template đã có hướng dẫn cho trường hợp "chỉ thấy diff".

## Template Variables

| Placeholder      | Nguồn                                                         |
| ---------------- | ------------------------------------------------------------- |
| `{coding_stack}` | `stacks/core/` + thư mục cha + `stacks/<STACK>/`              |
| `{coding_rules}` | `rules/<RULES_PATH>/` (đệ quy)                                |
| `{code_diff}`    | Luồng chính: hướng dẫn lấy diff · Luồng cũ: diff/chunk thật   |

- `stacks/` = luật **chung** theo công nghệ, dùng lại cho nhiều dự án (CORE + stack).
- `rules/` = luật **riêng** của dự án: cấu trúc, ranh giới tầng, luật có nhãn, nợ kỹ thuật đã biết. Luật dự án được ưu tiên hơn luật chung.

## Cấu trúc template

```
[Mục tiêu: chính xác, ít nhiễu, hành động được]
=== QUY TẮC CHUNG ===            {coding_stack}
=== KIẾN TRÚC & LUẬT RIÊNG ===   {coding_rules}
=== THỨ TỰ ƯU TIÊN ===           dự án (+ đặc thù repo trong CLAUDE.md) > chung > kinh nghiệm; cùng vi phạm khác nhãn → nhãn luật chung
=== PHẠM VI REVIEW ===           dòng +, dòng - (chỉ khi xoá cơ chế bảo vệ), bỏ file sinh tự động
=== XÁC MINH TRƯỚC KHI KẾT LUẬN === có công cụ → đọc file; chỉ có diff → không suy đoán "thiếu"
=== NHỮNG GÌ CẦN TÌM ===         bug → bảo mật → kiến trúc → xử lý lỗi → quy ước có nêu rõ
=== KHÔNG BÁO ===                context, nợ kỹ thuật, format, điều kiện "CHỈ áp dụng khi" không thoả
=== MỨC ĐỘ ===                   theo nhãn [chặn merge]/[cảnh báo]/[nit] = MUST/SHOULD/NOTE
=== TỰ KIỂM TRA ===              3 câu hỏi cho từng phát hiện
=== YÊU CẦU ĐẦU RA ===           format mục (Vấn đề/Sửa) + khối tổng kết bắt buộc + ví dụ
=== CODE DIFF ===                {code_diff}
```

## Viết luật sao cho AI review tốt và ít báo sai

1. **Gắn nhãn cho từng luật**: `[chặn merge]` (🔴) chỉ cho lỗi chắc chắn gây hỏng/bảo mật/vi phạm kiến trúc cứng; `[cảnh báo]` (⚠️); `[nit]` (💡). Dòng không nhãn là mô tả, AI không dùng để báo lỗi.
2. **Ghi điều kiện**: luật chỉ đúng trong hoàn cảnh nhất định thì viết "CHỈ áp dụng khi ...", ví dụ "CHỈ khi diff có `package.json`".
3. **Không yêu cầu "thiếu X" mơ hồ**: ghi rõ "CHỈ báo khi xác minh được" hoặc "dạng câu hỏi" cho các mục như `.env.example`, đăng ký route/job, key i18n, test.
4. **Mục "Ngoại lệ / nợ kỹ thuật đã biết"** trong mỗi `rules/<project>/ARCHITECTURE_RULES.md`: liệt kê chỗ code cũ sai có chủ đích. Mỗi lần dev đánh dấu một comment là báo sai lặp lại, thêm mẫu đó vào đây.
5. **Mục "Nguyên tắc khi AI sửa/sinh code"** là hướng dẫn sinh code, AI không dùng để báo lỗi review.
6. **Không nhập vai trong file luật** ("Bạn là ..."): file luật chỉ chứa danh sách luật; vai trò nằm ở template.
7. Muốn AI bắt thêm loại lỗi → sửa `stacks/` hoặc `rules/`, không nhồi vào template (template dùng chung mọi dự án).

## Cách tùy chỉnh

1. **Sửa template**: chỉnh file `.txt`, nhớ đồng bộ VI và EN, không thêm `{` `}`.
2. **Thêm stack**: tạo `stacks/<tên>/<file>.md`; biến thể TypeScript đặt trong `stacks/<tên>/typescript/` (thư mục cha được nạp kèm).
3. **Thêm dự án**: tạo `rules/<project>/ARCHITECTURE_RULES.md` theo khung: 1. Tổng quan · 2. Cấu trúc · 3. Luật review (có nhãn) · 4. Quy ước đặt tên · 5. Ngoại lệ / nợ kỹ thuật · 6. Nguyên tắc khi AI sửa/sinh code.
4. **Kiểm tra prompt cục bộ**:

```bash
ACTION_PATH=$(pwd) STACK=nextjs/typescript RULES_PATH=base-frontend \
REVIEW_LANGUAGE=vietnamese GITHUB_OUTPUT=/tmp/out \
bash scripts/system-prompts/build-prompt.sh && grep '^Source:' /tmp/out
```
