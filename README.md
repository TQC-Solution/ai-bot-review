# Flutter AI Code Reviewer (OpenRouter)

> **🎉 NEW: v3.0 - OpenRouter Integration!** Now supports multiple AI providers through OpenRouter API. Easily switch between models like Grok, Claude, GPT-4, Gemini, and more by just changing a config parameter. No more vendor lock-in!

## Dự án này làm gì?

**Đơn giản là**: Mỗi khi bạn tạo Pull Request (PR) trên GitHub, một AI sẽ tự động đọc code của bạn và đưa ra nhận xét, giống như một senior developer review code.

**Chi tiết hơn**:
- Đây là một GitHub Action (tự động chạy khi có PR)
- Sử dụng AI (như ChatGPT, Claude, Gemini...) để phân tích code Flutter/Dart
- Kiểm tra theo các quy tắc như Clean Architecture, GetX patterns, chuẩn code...
- Đưa ra **1 comment tổng hợp** trên PR với các góp ý cụ thể

**Ví dụ thực tế**:
```
Bạn tạo PR thêm tính năng login
↓
AI tự động review trong vài phút
↓
Bạn nhận được comment:
  "❌ File login_controller.dart: Nên dùng Get.find() thay vì Get.put()..."
  "✅ File login_screen.dart: Code đạt chuẩn"
```

## Features

- ✅ **200+ AI Models Support**: Use any model from OpenRouter (Grok, Claude, GPT-4, Gemini, Llama, Mistral, etc.)
- ✅ **Easy Model Switching**: Change AI provider with just one config parameter - no code changes needed
- ✅ **Free & Paid Options**: Choose from free models (Grok 4.1, Gemini 2.0) or premium ones (Claude 3.5, GPT-4)
- ✅ **Reasoning Support**: Enable advanced reasoning for supported models (e.g., Grok 4.1)
- ✅ **Request Tracking**: Automatically sends project name in `X-Title` header for usage tracking on OpenRouter dashboard
- ✅ **Intelligent Chunking**: Automatically splits large PRs (>5 files, >30k chars) into reviewable chunks to ensure complete coverage
- ✅ **Clean Architecture Review**: Validates layer dependencies and architectural patterns
- ✅ **GetX Best Practices**: Checks controller lifecycle and instance management
- ✅ **Type Safety**: Detects hardcoded assets and translation strings
- ✅ **Multi-language Support**: Review comments in Vietnamese or English
- ✅ **Modular Rule System**: Coding standards organized in separate rule files for easy maintenance
- ✅ **Single Consolidated Comment**: Posts one comprehensive review per PR to minimize noise
- ✅ **Automatic Retry**: Handles rate limits with exponential backoff

## Cách sử dụng (Dành cho người mới)

### Bước 1: Hiểu GitHub Action là gì

GitHub Action = **Một đoạn code tự động chạy khi có sự kiện trên GitHub**

Trong dự án này:
- **Sự kiện**: Khi có Pull Request mới hoặc cập nhật PR
- **Hành động**: Chạy script Python để review code bằng AI
- **Kết quả**: Đăng comment review lên PR

### Bước 2: Cài đặt nhanh (3 bước)

**Không cần biết Python!** Chỉ cần làm theo:

1. **Tạo file mới** trong repo của bạn: `.github/workflows/ai-review.yml`
   - Nếu chưa có thư mục `.github/workflows`, tạo mới nó

2. **Copy và paste** nội dung bên dưới vào file đó

3. **Lưu lại** - Xong! Không cần cài đặt gì thêm.

**File cấu hình (Copy toàn bộ đoạn này):**

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review

# Khi nào chạy? → Khi có PR mới hoặc cập nhật PR trên nhánh main/dev
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main, dev]

# Quyền cần thiết
permissions:
  contents: read           # Đọc code
  pull-requests: write     # Viết comment vào PR
  issues: write           # Viết comment (backup)

jobs:
  ai_review:
    name: AI Code Review
    runs-on: ubuntu-latest  # Chạy trên máy ảo Ubuntu

    steps:
      # Bước 1: Tải code về
      - name: Checkout source code
        uses: actions/checkout@v4

      # Bước 2: Chạy AI reviewer
      - name: Run OpenRouter AI Code Reviewer
        uses: pubstar-io/ios-sdk-ai-review-bot@main  # Dùng tool này
        with:
          openrouter-api-key: ${{ secrets.OPENROUTER_API_KEY }}  # API key (sẽ setup ở bước sau)
          github-token: ${{ secrets.GITHUB_TOKEN }}              # Token tự động có sẵn
          review-language: 'vietnamese'  # Ngôn ngữ review (vietnamese hoặc english)
```

### Bước 3: Lấy API Key và cấu hình

**3.1. Lấy OpenRouter API Key**

1. Vào [OpenRouter Keys](https://openrouter.ai/keys)
2. Đăng ký tài khoản (miễn phí)
3. Click "Create Key" → Tạo API key mới
4. **Copy key này** (chỉ hiển thị 1 lần, nếu mất phải tạo lại)
5. *(Tùy chọn)* Nạp tiền nếu dùng AI trả phí, **hoặc dùng AI miễn phí** (Grok, Gemini)

**3.2. Lưu API Key vào GitHub Secret**

1. Vào repo của bạn trên GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click nút **"New repository secret"**
4. Điền:
   - **Name**: `OPENROUTER_API_KEY` (phải đúng tên này)
   - **Value**: Paste API key bạn copy ở bước 3.1
5. Click **"Add secret"**

**3.3. Tạo Pull Request để test**
   - Tạo 1 PR bất kỳ → Action sẽ tự động chạy và review
   - Xem kết quả trong tab "Checks" hoặc comment của PR

---

## Cách đổi AI Model (Dành cho người quản lý dự án)

### AI Model là gì?

Mỗi model có:
- **Độ thông minh khác nhau** (model đắt tiền thường thông minh hơn)
- **Chi phí khác nhau** (có model miễn phí, có model trả phí)
- **Tốc độ khác nhau**

### Model hiện tại

Dự án đang dùng: **Grok 4.1 Fast (Free)**
- ✅ Miễn phí
- ✅ Nhanh
- ✅ Hỗ trợ reasoning (suy luận nâng cao)

### Cách đổi model

> **Lưu ý**: Chỉ người quản lý dự án mới có thể đổi model (user thường không đổi được)

**Bước 1**: Mở file [`scripts/reviewer/config.py`](scripts/reviewer/config.py)

**Bước 2**: Tìm dòng 28, sửa giá trị `OPENROUTER_MODEL`:

```python
# Dòng 28 trong config.py
OPENROUTER_MODEL = "x-ai/grok-4.1-fast:free"  # ← Đổi giá trị này

# Ví dụ các model có thể dùng:
# ┌─────────────────────────────────────┬──────────┬──────────────┐
# │ Model                               │ Loại    │ Đặc điểm     │
# ├─────────────────────────────────────┼──────────┼──────────────┤
# │ "x-ai/grok-4.1-fast:free"          │ FREE    │ Nhanh        │
# │ "google/gemini-2.0-flash-exp:free" │ FREE    │ Thông minh   │
# │ "anthropic/claude-3.5-sonnet"      │ PAID    │ Rất thông minh│
# │ "openai/gpt-4-turbo"               │ PAID    │ Đa năng      │
# └─────────────────────────────────────┴──────────┴──────────────┘
```

**Bước 3**: Lưu file và commit

**Bước 4**: Xem danh sách đầy đủ tại [OpenRouter Model List](https://openrouter.ai/models)

---

## Tùy chỉnh cấu hình

### Các tham số có thể thay đổi

Trong file `.github/workflows/ai-review.yml`, phần `with:` có các tham số sau:

| Tham số | Bắt buộc? | Mặc định | Giải thích |
|---------|-----------|----------|------------|
| `openrouter-api-key` | ✅ Bắt buộc | - | API key của OpenRouter (đã setup ở bước 3) |
| `github-token` | ✅ Bắt buộc | - | Token GitHub (dùng `${{ secrets.GITHUB_TOKEN }}` - tự động có) |
| `review-language` | ⭕ Tùy chọn | `vietnamese` | Ngôn ngữ review: `vietnamese` hoặc `english` |

### Ví dụ: Đổi sang review bằng tiếng Anh

Sửa file `.github/workflows/ai-review.yml`:

```yaml
- uses: pubstar-io/ios-sdk-ai-review-bot@main
  with:
    openrouter-api-key: ${{ secrets.OPENROUTER_API_KEY }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    review-language: 'english'  # ← Đổi thành 'english'
```

---

## AI sẽ review những gì?

### Các quy tắc AI kiểm tra

AI được huấn luyện để kiểm tra code Flutter/Dart theo các tiêu chí sau:

#### 1. **Kiến trúc Clean Architecture**

   **Là gì?** Cách tổ chức code thành các tầng (layers) rõ ràng

   **AI kiểm tra:**
   - ❌ Tầng Domain có import code từ tầng Data/Presentation không?
   - ❌ Có vi phạm nguyên tắc phụ thuộc giữa các tầng không?

   **Ví dụ lỗi:**
   ```dart
   // File: domain/usecases/login_usecase.dart
   import '../../data/repositories/user_repo.dart'; // ❌ SAI: Domain không được import Data
   ```

#### 2. **GetX Controller Management**

   **Là gì?** Cách quản lý state với GetX framework

   **AI kiểm tra:**
   - ❌ Dùng `Get.put()` sai chỗ (nên dùng `Get.find()`)
   - ❌ Controller lifecycle không đúng

   **Ví dụ lỗi:**
   ```dart
   // Trong Widget build()
   final controller = Get.put(LoginController()); // ❌ SAI: Sẽ tạo instance mới mỗi lần build
   // ✅ ĐÚNG: Get.find<LoginController>()
   ```

#### 3. **Type Safety (An toàn kiểu dữ liệu)**

   **AI kiểm tra:**
   - ❌ Hardcode đường dẫn assets → Nên dùng `Assets.icons.iconName`
   - ❌ Hardcode text UI → Nên dùng `context.tr()` để hỗ trợ đa ngôn ngữ

   **Ví dụ lỗi:**
   ```dart
   Image.asset('assets/icons/logo.png')  // ❌ SAI: Hardcode
   Image.asset(Assets.icons.logo)        // ✅ ĐÚNG

   Text('Login')              // ❌ SAI: Hardcode
   Text(context.tr('login'))  // ✅ ĐÚNG
   ```

#### 4. **Error Handling (Xử lý lỗi)**

   **AI kiểm tra:**
   - ❌ Thiếu pattern `Either<Failure, T>` (functional programming)
   - ❌ Throw exception thô thay vì dùng Failure types

   **Ví dụ:**
   ```dart
   // ❌ SAI
   User getUser() {
     throw Exception('User not found');
   }

   // ✅ ĐÚNG
   Either<Failure, User> getUser() {
     return Left(UserNotFoundFailure());
   }
   ```

#### 5. **Naming Conventions (Quy tắc đặt tên)**

   **AI kiểm tra:**
   - File names: `snake_case` (vd: `user_profile.dart`)
   - Class names: `PascalCase` (vd: `UserProfile`)
   - Variables/methods: `camelCase` (vd: `userName`, `getUserName()`)

#### 6. **Code Quality (Chất lượng code)**

   **AI kiểm tra:**
   - 🐛 Bugs và lỗi logic
   - 📖 Dễ đọc, dễ maintain không
   - ⚡ Performance có vấn đề không

---

## Hiểu cấu trúc dự án (Dành cho người muốn tùy chỉnh)

### Tổng quan luồng hoạt động

```
┌─────────────────────────────────────────────────────────────┐
│  1. User tạo Pull Request trên GitHub                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  2. GitHub Actions tự động kích hoạt                        │
│     → Chạy file .github/workflows/ai-review.yml            │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Action gọi script Python: scripts/ai_review.py         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Script Python làm gì?                                   │
│     a) Lấy code diff từ PR (github_client.py)              │
│     b) Đọc các quy tắc review (prompt_builder.py)         │
│     c) Gửi code + quy tắc cho AI (openrouter_client.py)   │
│     d) Nhận kết quả review từ AI                           │
│     e) Post comment lên PR (github_client.py)              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  5. User thấy comment AI review trên PR                     │
└─────────────────────────────────────────────────────────────┘
```

### Cấu trúc thư mục (Dễ hiểu)

```
flutter-ai-review-bot/
│
├── action.yml                           # ← File định nghĩa GitHub Action
│
├── .github/workflows/
│   └── ai-review.yml                   # ← File workflow mẫu (user sẽ copy file này)
│
├── scripts/                             # ← Code Python (core của dự án)
│   │
│   ├── ai_review.py                    # ← File chính - điều phối toàn bộ
│   │
│   ├── reviewer/                       # ← Package chứa các modules
│   │   ├── config.py                  # → Đọc cấu hình (API key, model...)
│   │   ├── github_client.py           # → Tương tác với GitHub API
│   │   ├── openrouter_client.py       # → Gọi AI qua OpenRouter
│   │   ├── prompt_builder.py          # → Xây dựng prompt gửi cho AI
│   │   ├── diff_chunker.py            # → Chia nhỏ PR lớn thành chunks
│   │   └── utils.py                   # → Các hàm tiện ích
│   │
│   ├── requirements.txt                # ← Danh sách thư viện Python cần cài
│   │
│   ├── rule/                           # ← Các quy tắc review (có thể edit)
│   │   ├── CLEAN_ARCHITECTURE_RULES.md # → Quy tắc Clean Architecture
│   │   ├── GETX_CONTROLLER_RULES.md    # → Quy tắc GetX
│   │   └── CODING_RULES.md             # → Quy tắc code chung
│   │
│   └── prompts/                        # ← Template prompt gửi AI (có thể edit)
│       ├── review_prompt_vi.txt        # → Prompt tiếng Việt
│       ├── review_prompt_en.txt        # → Prompt tiếng Anh
│       └── README.md                   # → Hướng dẫn edit prompts
│
└── README.md                            # ← File này (hướng dẫn sử dụng)
```

**Giải thích từng phần:**

| Thư mục/File | Chức năng | Có thể chỉnh sửa? |
|--------------|-----------|-------------------|
| `action.yml` | Định nghĩa GitHub Action | ❌ Không (trừ khi bạn là maintainer) |
| `.github/workflows/ai-review.yml` | File mẫu để user copy | ✅ Có (user copy và tùy chỉnh) |
| `scripts/ai_review.py` | Code Python chính | ❌ Không cần (trừ khi fix bug) |
| `scripts/reviewer/*.py` | Các module Python | ❌ Không cần (trừ khi fix bug) |
| `scripts/rule/*.md` | **Quy tắc review** | ✅ **Có - Edit để thay đổi cách AI review** |
| `scripts/prompts/*.txt` | **Template prompt AI** | ✅ **Có - Edit để thay đổi tone/style của AI** |

### Chi tiết các module Python

**Dự án được tổ chức thành 6 modules nhỏ**, mỗi module làm 1 nhiệm vụ riêng:

#### Module chính
- **[ai_review.py](scripts/ai_review.py)** - File điều phối chính
  - Gọi các module khác theo thứ tự
  - Xử lý workflow tổng thể
  - Code ngắn gọn, dễ đọc

#### Các module con (trong `scripts/reviewer/`)

1. **[config.py](scripts/reviewer/config.py)** - Quản lý cấu hình
   - Đọc biến môi trường (API keys, tokens...)
   - Kiểm tra cấu hình hợp lệ
   - Định nghĩa các hằng số (giới hạn kích thước, token...)

2. **[github_client.py](scripts/reviewer/github_client.py)** - Làm việc với GitHub
   - Lấy thông tin PR (metadata, code diff)
   - Đăng comment review lên PR
   - Kiểm tra cấu trúc diff hợp lệ

3. **[openrouter_client.py](scripts/reviewer/openrouter_client.py)** - Gọi AI
   - Kết nối với OpenRouter API
   - Hỗ trợ 200+ AI models
   - Xử lý retry khi bị rate limit
   - Hỗ trợ reasoning cho model nâng cao
   - Tự động gửi tên project trong header `X-Title` để tracking usage

4. **[prompt_builder.py](scripts/reviewer/prompt_builder.py)** - Xây dựng prompt
   - Load template prompt (tiếng Việt/Anh)
   - Load các quy tắc coding
   - Kết hợp thành prompt hoàn chỉnh gửi AI
   - Cắt ngắn diff nếu quá dài

5. **[diff_chunker.py](scripts/reviewer/diff_chunker.py)** - Chia nhỏ PR lớn
   - Tự động phát hiện PR quá lớn (>5 files, >30k ký tự)
   - Chia diff thành các chunks nhỏ (theo file)
   - Đảm bảo AI không bỏ sót code

6. **[utils.py](scripts/reviewer/utils.py)** - Hàm tiện ích
   - Parse số PR từ GitHub ref
   - Format error messages
   - Các helper functions khác

#### Ưu điểm của kiến trúc này
- ✅ **Modular**: Mỗi module làm 1 việc, dễ hiểu
- ✅ **Dễ test**: Test từng module riêng biệt
- ✅ **Dễ maintain**: Sửa bug dễ dàng, biết bug ở module nào
- ✅ **Dễ mở rộng**: Thêm AI provider mới chỉ cần sửa 1 file
- ✅ **Tương thích ngược**: User cũ không cần thay đổi gì

#### Tài liệu chi tiết

Nếu bạn muốn hiểu sâu hơn hoặc đóng góp code:
- 📖 [Module Documentation](scripts/reviewer/README.md) - Chi tiết từng module
- 📖 [Architecture Diagrams](scripts/reviewer/ARCHITECTURE.md) - Sơ đồ kiến trúc

---

## Test local (Dành cho developer muốn chạy thử)

### Khi nào cần test local?

- Bạn muốn thử nghiệm trước khi push lên GitHub
- Bạn đang sửa code Python và muốn test
- Bạn muốn hiểu cách script hoạt động

### Các bước test trên máy local

**Bước 1: Cài đặt Python dependencies**

```bash
# Cài các thư viện Python cần thiết
pip install -r scripts/requirements.txt
```

**Bước 2: Set biến môi trường**

```bash
# Các thông tin cần thiết cho script
export GITHUB_REF='refs/pull/1/merge'              # ← Số PR (ví dụ: PR #1)
export GITHUB_TOKEN='ghp_xxxxxxxxxxxxx'            # ← GitHub Personal Access Token
export GITHUB_REPOSITORY='owner/repo'             # ← Tên repo (vd: facebook/react)
export OPENROUTER_API_KEY='sk-or-v1-xxxxxx'      # ← API key OpenRouter
export REVIEW_LANGUAGE='vietnamese'               # ← Ngôn ngữ (vietnamese hoặc english)
```

> **Lấy GitHub Token ở đâu?**
> 1. Vào GitHub → Settings → Developer settings → Personal access tokens
> 2. Generate new token với quyền: `repo`, `pull_request`

**Bước 3: Chạy script**

```bash
# Chạy file Python chính
python scripts/ai_review.py
```

**Kết quả**: Script sẽ review PR và in ra kết quả (hoặc post comment nếu có quyền)

---

## Tùy chỉnh quy tắc review

### Quy tắc review được lưu ở đâu?

Tất cả quy tắc được lưu trong thư mục `scripts/rule/` dưới dạng file Markdown (`.md`)

Hiện có 3 file quy tắc:
- **[CLEAN_ARCHITECTURE_RULES.md](scripts/rule/CLEAN_ARCHITECTURE_RULES.md)** - Quy tắc Clean Architecture
- **[GETX_CONTROLLER_RULES.md](scripts/rule/GETX_CONTROLLER_RULES.md)** - Quy tắc GetX
- **[CODING_RULES.md](scripts/rule/CODING_RULES.md)** - Quy tắc code chung (naming, assets, i18n...)

### Cách chỉnh sửa quy tắc

**Cách 1: Sửa file quy tắc có sẵn**

Ví dụ muốn thay đổi quy tắc GetX:

1. Mở file `scripts/rule/GETX_CONTROLLER_RULES.md`
2. Sửa nội dung theo ý muốn (bằng tiếng Việt hoặc tiếng Anh đều được)
3. Lưu file
4. Lần review sau AI sẽ dùng quy tắc mới

**Cách 2: Thêm file quy tắc mới**

Ví dụ muốn thêm quy tắc về testing:

1. Tạo file mới: `scripts/rule/TESTING_RULES.md`
2. Viết quy tắc:
   ```markdown
   # Testing Rules

   - Every feature must have unit tests
   - Coverage must be > 80%
   - Use mockito for mocking
   ```
3. Lưu file → Tự động được load vào prompt gửi AI

> **Lưu ý**: Tất cả file `.md` trong thư mục `rule/` sẽ được AI đọc và áp dụng

---

## Tùy chỉnh prompt gửi AI

### Prompt được lưu ở đâu?

Thư mục `scripts/prompts/` có 2 file:
- `review_prompt_vi.txt` - Prompt tiếng Việt
- `review_prompt_en.txt` - Prompt tiếng Anh

### Cách chỉnh sửa prompt

**Ví dụ: Muốn AI review strict hơn**

1. Mở file `scripts/prompts/review_prompt_vi.txt`
2. Tìm đoạn:
   ```
   Bạn là một senior Flutter/Dart engineer...
   ```
3. Sửa thành:
   ```
   Bạn là một SUPER STRICT senior Flutter/Dart engineer.
   Hãy tìm MỌI lỗi, dù là nhỏ nhất.
   Đánh giá rất khắt khe...
   ```
4. Lưu file

**Biến template có thể dùng:**

Trong prompt, bạn có thể dùng các biến này (sẽ được thay thế tự động):
- `{coding_rules}` → Nội dung từ các file trong `scripts/rule/`
- `{code_diff}` → Code diff của PR

**Ví dụ prompt:**
```txt
Bạn là AI reviewer.
Review code sau theo các quy tắc:

{coding_rules}

Code cần review:
{code_diff}
```

> **Chi tiết**: Xem hướng dẫn đầy đủ tại [scripts/prompts/README.md](scripts/prompts/README.md)

---

## Chi phí sử dụng API

#### 🆓 Models miễn phí (Free)
- **Grok 4.1 Fast** (đang dùng) - Hoàn toàn miễn phí
- **Gemini 2.0 Flash** - Miễn phí
- **Llama 3.2** - Miễn phí

→ **Bạn có thể dùng KHÔNG MẤT TIỀN** nếu chọn model free

#### 💰 Models trả phí (Paid)
- **Claude 3.5 Sonnet** - ~$0.01-0.02 mỗi lần review (rất rẻ)
- **GPT-4 Turbo** - ~$0.02-0.05 mỗi lần review

→ Nếu chọn model trả phí, phải nạp tiền vào OpenRouter trước

### Kiểm soát chi phí

Action tự động:
- ✅ Retry khi bị rate limit (giới hạn số lần gọi)
- ✅ Xử lý lỗi API một cách graceful
- ✅ Hỗ trợ reasoning cho model có tính năng này

### Xem usage của bạn

- **Dashboard**: [OpenRouter Activity](https://openrouter.ai/activity)
- **So sánh model**: [OpenRouter Models](https://openrouter.ai/models)

**Khuyến nghị**: Dùng model miễn phí cho dự án cá nhân, model trả phí cho production

---

## OpenRouter Request Tracking

Action tự động gửi thông tin project trong mỗi API request để giúp bạn tracking và phân loại usage trên OpenRouter dashboard.

### Cách hoạt động

Mỗi request gửi đến OpenRouter sẽ bao gồm header `X-Title` với tên repository và số PR:

```http
POST https://openrouter.ai/api/v1/chat/completions
Headers:
  Authorization: Bearer sk-or-v1-...
  Content-Type: application/json
  X-Title: your-company/your-app - PR #123  ← Tên repo + PR number
```

### Lợi ích

- 📊 **Theo dõi usage theo project và PR**: Xem chi tiêu của từng repo và từng PR riêng biệt trên [OpenRouter Activity](https://openrouter.ai/activity)
- 🔍 **Debug dễ dàng**: Biết request nào thuộc PR nào khi có lỗi
- 💰 **Quản lý chi phí**: Phân tích cost breakdown theo từng dự án và PR cụ thể

### Tùy chỉnh tên hiển thị

Nếu muốn thay đổi tên hiển thị (mặc định là `GITHUB_REPOSITORY - PR #<number>`):

1. Mở file [`scripts/ai_review.py`](scripts/ai_review.py)
2. Tìm dòng 56-60:
   ```python
   openrouter_client = OpenRouterClient(
       Config.OPENROUTER_API_KEY,
       project_name=Config.GITHUB_REPOSITORY or "AI Code Review Bot",
       pr_number=pr_number
   )
   ```
3. Thay đổi theo ý muốn:
   - Bỏ PR number: Xóa dòng `pr_number=pr_number`
   - Đổi project name: Thay `Config.GITHUB_REPOSITORY` thành tên tùy chỉnh

---

## Xử lý PR lớn

**Action tự động chia nhỏ PR lớn thành các chunks (phần)**

#### Khi nào chunking được kích hoạt?

- PR có **>5 files** VÀ **>30,000 ký tự**
- Tự động chia theo file (không bao giờ cắt giữa file)
- Review từng chunk riêng, sau đó gộp lại

#### Ưu điểm

- ✅ **Review đầy đủ**: Tất cả file đều được review, không bỏ sót
- ✅ **Tránh "Lost in the Middle"**: AI tập trung tốt hơn khi context ngắn
- ✅ **Chất lượng cao hơn**: AI chỉ focus vào 2-4 files mỗi lần
- ✅ **Theo dõi tiến độ**: Log hiển thị "Reviewing chunk 2/5..."

### Ví dụ output khi có chunking

Với PR lớn, bạn sẽ thấy comment như sau:

```markdown
## 📋 Tổng Hợp Code Review

_PR này được review theo 3 phần do kích thước lớn._

---

### Phần 1: lib/features/auth/login.dart, logout.dart
🔴 Lỗi Nghiêm Trọng
- File login.dart dòng 42: Dùng Get.put() trong build()
...

---

### Phần 2: lib/features/profile/user_profile.dart
⚠️ Cảnh báo
- File user_profile.dart dòng 15: Hardcode string 'Profile'
...

---

### Phần 3: lib/core/utils/...
✅ Tốt
...
```

**Lưu ý**: Chunking sẽ gọi API nhiều lần hơn (1 lần mỗi chunk), nhưng đảm bảo review đầy đủ

---

## Xử lý lỗi (Troubleshooting)

### ❌ Lỗi: "OPENROUTER_API_KEY not set"

**Nguyên nhân**: Chưa thêm API key vào GitHub Secrets

**Cách fix**:
1. Vào repo → Settings → Secrets and variables → Actions
2. Thêm secret tên `OPENROUTER_API_KEY`
3. Paste API key vào

### ❌ Lỗi: "Invalid API key (401)"

**Nguyên nhân**: API key sai hoặc hết hạn

**Cách fix**:
1. Kiểm tra lại API key tại [OpenRouter Keys](https://openrouter.ai/keys)
2. Đảm bảo tên secret là **chính xác**: `OPENROUTER_API_KEY` (không có dấu cách, đúng chữ hoa/thường)
3. Tạo API key mới nếu cần

### ❌ Lỗi: "Insufficient credits (402)"

**Nguyên nhân**: Hết tiền (khi dùng model trả phí)

**Cách fix**:
- **Option 1**: Nạp tiền tại [OpenRouter Credits](https://openrouter.ai/credits)
- **Option 2**: Đổi sang model miễn phí (xem phần [Cách đổi AI Model](#cách-đổi-ai-model-dành-cho-người-quản-lý-dự-án))

### ⚠️ Cảnh báo: "PR diff is empty"

**Nguyên nhân**: PR không có thay đổi code nào

**Giải thích**: Bình thường, không phải lỗi. PR trống nên không có gì để review.

### ⏱️ Lỗi: "Rate limit exceeded (429)"

**Nguyên nhân**: Gọi API quá nhiều lần trong thời gian ngắn

**Cách fix**:
- Đợi 1-2 phút rồi thử lại (action tự động retry)
- Kiểm tra rate limit tại [OpenRouter Settings](https://openrouter.ai/settings/limits)

### 🤔 Lỗi: "AI says file doesn't exist" hoặc "Missing code review"

**Đã fix trong version mới**:
- ✅ Smart Truncation: Cắt diff theo file, không cắt giữa file
- ✅ Intelligent Chunking: PR lớn tự động chia nhỏ
- ✅ Tăng giới hạn: Từ 12k → 100k ký tự

**Nếu vẫn gặp lỗi**:
1. Kiểm tra GitHub Actions logs (tab "Actions" trong repo)
2. Tìm thông tin về chunking
3. Báo lỗi tại [GitHub Issues](https://github.com/anthropics/claude-code/issues)

## License

MIT License - Feel free to use and modify for your projects

## Contributing

Contributions welcome! Please open an issue or PR.

## Credits

Built with:
- [OpenRouter API](https://openrouter.ai/) - Unified access to 200+ AI models
- [GitHub Actions](https://github.com/features/actions)

## Migration from Gemini

If you're upgrading from the Gemini version (v2.x), just update your workflow:

**Old (Gemini):**
```yaml
- uses: pubstar-io/ios-sdk-ai-review-bot@v2
  with:
    gemini-api-key: ${{ secrets.GEMINI_API_KEY }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

**New (OpenRouter):**
```yaml
- uses: pubstar-io/ios-sdk-ai-review-bot@main
  with:
    openrouter-api-key: ${{ secrets.OPENROUTER_API_KEY }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

**Note**: Model selection is now controlled by project maintainers in `config.py`, not by workflow configuration. This ensures consistent review quality across all PRs.

