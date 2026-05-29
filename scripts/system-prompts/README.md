# Review Prompt Templates

This directory contains AI review prompt templates for different languages.

## Files

- **`review_prompt_vi.txt`** - Vietnamese review prompt template
- **`review_prompt_en.txt`** - English review prompt template

## Template Variables

Each prompt template uses the following placeholders:

- `{coding_stack}` - Replaced with combined content from all `.md` files in the selected stack folder under `scripts/stacks/<STACK>/` (e.g. `expressjs`, `nextjs/typescript`)
- `{coding_rules}` - Replaced with combined content from all `.md` rule files in `scripts/rules/<RULES_PATH>/` directory
- `{code_diff}` - Replaced with the actual code diff from the pull request

> Lưu ý: Template được thiết kế dùng chung cho MỌI stack/rule. Phần kiến thức đặc thù theo công nghệ
> được nạp động qua `{coding_stack}` và `{coding_rules}`; phần thân prompt chỉ chứa tiêu chí và
> format trung lập, không gắn với một ngôn ngữ/framework cụ thể.

## How to Customize

1. **Edit existing templates**: Modify the `.txt` files directly to change the review instructions
2. **Add new language**: Create a new file like `review_prompt_ja.txt` and update `ai_review.py` to support it

## Template Structure

Each template should follow this structure:

```
[Role Definition]

=== CODING STACK OF PROJECT ===
{coding_stack}

=== CODING RULES & STANDARDS ===
{coding_rules}

=== YOUR TASK ===
[Instructions for what to review - stack-neutral criteria]

[Requirements and formatting guidelines]

[Example format with emojis - generic placeholders, no specific language/framework]

=== CODE DIFF TO REVIEW ===
{code_diff}
```

2. Update `ai_review.py`:
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

## Benefits

- ✅ **Easy to read**: Plain text format without Python string escaping
- ✅ **Easy to edit**: No need to modify Python code to change prompts
- ✅ **Version control**: Track prompt changes separately from code logic
- ✅ **Collaboration**: Non-developers can update prompts
- ✅ **Testing**: Easy to compare different prompt versions
