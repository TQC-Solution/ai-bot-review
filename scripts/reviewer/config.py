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
    RULES_PATH = os.getenv("RULES_PATH", "empty")
    STACK = os.getenv("STACK")

    # OpenRouter model configuration
    # Model is controlled by project maintainers, users cannot override
    # Change this value here to switch models:
    # Free options:
    #   - "x-ai/grok-4.1-fast:free" (Free, fast, supports reasoning)
    #   - "google/gemini-2.0-flash-exp:free" (Free, high quality)
    # Paid options:
    #   - "anthropic/claude-3.5-sonnet" (Excellent for code review)
    #   - "openai/gpt-4-turbo" (High quality)
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-3.1-flash-lite")

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

    @classmethod
    def get_rules_path(cls) -> Path:
        """Lấy đường dẫn tuyệt đối đến thư mục chứa rules (scripts/rules/[rules])."""
        # __file__ trỏ tới: scripts/reviewer/config.py
        # .parent lần 1 ra: scripts/reviewer/
        # .parent lần 2 ra: scripts/
        scripts_dir = Path(__file__).resolve().parent.parent
        
        # Trỏ tới thư mục pubstar-ios nằm trong folter scripts/rules/
        return scripts_dir / "rules" / cls.RULES_PATH
    
    @classmethod
    def get_stacks_path(cls) -> Path:
        """Lấy đường dẫn tuyệt đối đến thư mục chứa stacks (scripts/stacks/)."""
        # __file__ trỏ tới: scripts/reviewer/config.py
        # .parent lần 1 ra: scripts/reviewer/
        # .parent lần 2 ra: scripts/
        scripts_dir = Path(__file__).resolve().parent.parent
        
        # Trỏ tới thư mục pubstar-ios nằm trong folter scripts/stacks/
        return scripts_dir / "stacks" / cls.STACK

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

        if not cls.STACK:
            errors.append("STACK is not set")

        if cls.REVIEW_LANGUAGE not in ['vietnamese', 'english']:
            errors.append(f"Invalid REVIEW_LANGUAGE: {cls.REVIEW_LANGUAGE}. Must be 'vietnamese' or 'english'")

        stacks_path = cls.get_stacks_path()
        if not stacks_path.exists() or not stacks_path.is_dir():
            errors.append(f"Stack directory not found at: {cls.STACK}")
        else:
            # Tìm tất cả file kết thúc bằng .md ở ngay trong thư mục này
            md_files = list(stacks_path.glob("*.md"))

            print(f"Debug: Checking md files: {len(md_files)} found in {stacks_path}")
            if not md_files:
                errors.append(f"Stacks directory '{cls.STACK}' contains no markdown (.md) files.")

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
