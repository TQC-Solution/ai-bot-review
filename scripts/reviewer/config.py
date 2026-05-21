"""Configuration management for AI code reviewer.

Handles environment variables and constants used across the application.
"""

import os
from pathlib import Path


class Config:
    """Configuration class for managing environment variables and constants."""

    # Environment variables
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
    GITHUB_REF = os.getenv("GITHUB_REF", "")
    REVIEW_LANGUAGE = os.getenv("REVIEW_LANGUAGE", "vietnamese").lower()
    # RULES_DIR = os.getenv("INPUT_RULES_PATH", "ai-review-rules")
    RULES_DIR = os.getenv("INPUT_RULES_PATH", "pubstar-ios")

    # OpenRouter model configuration
    # Model is controlled by project maintainers, users cannot override
    # Change this value here to switch models:
    # Free options:
    #   - "x-ai/grok-4.1-fast:free" (Free, fast, supports reasoning)
    #   - "google/gemini-2.0-flash-exp:free" (Free, high quality)
    # Paid options:
    #   - "anthropic/claude-3.5-sonnet" (Excellent for code review)
    #   - "openai/gpt-4-turbo" (High quality)
    OPENROUTER_MODEL = "z-ai/glm-4.5-air:free"
    # OPENROUTER_MODEL = "google/gemini-3.1-flash-lite"

    # Constants
    MAX_DIFF_LENGTH = 100000  # Limit diff size to avoid huge token payloads (increased from 12k)
    MAX_COMMENT_LENGTH = 60000  # GitHub has 65,536 char limit, use 60k for safety
    COMMENT_HEADER = "🤖 **AI Code Review (OpenRouter)**\n\n"

    # Diff processing settings
    WARN_DIFF_TRUNCATED = True  # Warn in prompt if diff was truncated

    # OpenRouter generation settings
    GENERATION_CONFIG = {
        "temperature": 0.6,
        "top_p": 0.95,
        "max_output_tokens": 32000,  # Max tokens for response
    }

    # Enable reasoning for supported models (e.g., grok-4.1-fast)
    # This is controlled by project, users cannot override
    ENABLE_REASONING = True  # Set to False to disable reasoning

    # Retry configuration
    MAX_RETRIES = 2
    INITIAL_RETRY_DELAY = 5  # seconds
    RETRY_BACKOFF_MULTIPLIER = 2

    # @classmethod
    # def get_rules_path(cls) -> Path:
    #     """Lấy đường dẫn tuyệt đối đến thư mục chứa rules."""
    #     # workspace_path = os.getenv("GITHUB_WORKSPACE", ".")
    #     # return Path(workspace_path) / cls.RULES_DIR
    #     script_dir = os.path.dirname(os.path.dirname(__file__))
    #     # return os.path.join(
    #     #         script_dir, "prompts", cls.RULES_DIR
    #     #     )
    #     return os.path.join(
    #             script_dir, "prompts", "pubstar-ios"
    #         )

    # @classmethod
    # def get_rules_path(cls) -> Path:
    #     """Lấy đường dẫn tuyệt đối đến thư mục chứa rules."""
    #     # Lấy thư mục chứa file hiện tại rồi lùi lên 2 cấp (tương đương 2 lần dirname)
    #     script_dir = Path(__file__).resolve().parent.parent
        
    #     # Đảm bảo rules_dir không bị None. Nếu None, gán một chuỗi an toàn.
    #     # Lưu ý: Thay ".github/ai-review-rules" bằng thư mục mặc định thực tế của bạn.
    #     rules_dir = cls.RULES_DIR
        
    #     # Dùng toán tử / của pathlib để nối đường dẫn một cách an toàn và trả về đúng object Path
    #     return script_dir / "prompts" / rules_dir

    @classmethod
    def get_rules_path(cls) -> Path:
        """Lấy đường dẫn tuyệt đối đến thư mục chứa rules (scripts/pubstar-ios)."""
        # __file__ trỏ tới: scripts/reviewer/config.py
        # .parent lần 1 ra: scripts/reviewer/
        # .parent lần 2 ra: scripts/
        scripts_dir = Path(__file__).resolve().parent.parent
        
        # Trỏ tới thư mục pubstar-ios nằm cùng cấp với reviewer
        return scripts_dir / "pubstar-ios"

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration.

        Returns:
            List of validation error messages. Empty if valid.
        """
        errors = []

        if not cls.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is not set")

        if not cls.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN is not set")

        if not cls.GITHUB_REPOSITORY:
            errors.append("GITHUB_REPOSITORY is not set")

        if not cls.RULES_DIR:
            errors.append("RULES_DIR is not set")

        if cls.REVIEW_LANGUAGE not in ['vietnamese', 'english']:
            errors.append(f"Invalid REVIEW_LANGUAGE: {cls.REVIEW_LANGUAGE}. Must be 'vietnamese' or 'english'")

        rules_path = cls.get_rules_path()

        if not rules_path.exists() or not rules_path.is_dir():
            errors.append(f"Rules directory not found at: {cls.RULES_DIR}")
        else:
            # Tìm tất cả file kết thúc bằng .md ở ngay trong thư mục này
            md_files = list(rules_path.glob("*.md"))
            if not md_files:
                errors.append(f"Rules directory '{cls.RULES_DIR}' contains no markdown (.md) files.")

        return errors

    @classmethod
    def print_debug_info(cls):
        """Print configuration for debugging (with masked secrets)."""
        print("=" * 60)
        print("🔍 Environment Variables Check:")
        print("=" * 60)
        print(f"   GITHUB_REF:           {cls.GITHUB_REF or '❌ NOT SET'}")
        print(f"   GITHUB_REPOSITORY:    {cls.GITHUB_REPOSITORY or '❌ NOT SET'}")
        print(f"   GITHUB_TOKEN:         {'✅ SET (' + cls.GITHUB_TOKEN[:8] + '...)' if cls.GITHUB_TOKEN else '❌ NOT SET'}")
        print(f"   OPENROUTER_API_KEY:   {'✅ SET' if cls.OPENROUTER_API_KEY else '❌ NOT SET'}")
        print(f"   OPENROUTER_MODEL:     {cls.OPENROUTER_MODEL} (configured in code)")
        print(f"   REVIEW_LANGUAGE:      {cls.REVIEW_LANGUAGE}")
        print(f"   ENABLE_REASONING:     {cls.ENABLE_REASONING} (configured in code)")
        print("=" * 60)
        print()
