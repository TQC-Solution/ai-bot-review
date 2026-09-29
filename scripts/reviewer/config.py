"""Configuration management for AI code reviewer.

Handles environment variables and constants used across the application.
"""

import os
from pathlib import Path


class Config:
    """Configuration class for managing environment variables and constants."""

    # CI still passes openrouter-api-key / secrets.OPENROUTER_API_KEY.
    # The secret value must be a Cursor API key (cursor_... or crsr_...).
    CURSOR_API_KEY = (
        os.getenv("CURSOR_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
    )
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
    GITHUB_REF = os.getenv("GITHUB_REF", "")
    REVIEW_LANGUAGE = os.getenv("REVIEW_LANGUAGE", "vietnamese").lower()
    RULES_PATH = os.getenv("RULES_PATH", "empty")
    STACK = os.getenv("STACK")

    # Temporarily skip calling Cursor so consumer CI stays green while the
    # API token / quota is unavailable. Set back to False to resume reviews.
    REVIEW_PAUSED = True
    # Must be a model ID from Cursor.models.list() for the API key's account.
    #   - "composer-2.5"       (Cursor included pool — cheaper, more weekly usage)
    #   - "claude-sonnet-5"    (Other Models pool — burns Pro quota faster)
    #   - "auto"               (Let Cursor pick)
    CURSOR_MODEL = "composer-2.5"

    # Constants
    MAX_DIFF_LENGTH = 100000  # Limit diff size to avoid huge token payloads (increased from 12k)
    MAX_COMMENT_LENGTH = 60000  # GitHub has 65,536 char limit, use 60k for safety
    COMMENT_HEADER = "🤖 **AI Code Review**\n\n"

    # Diff processing settings
    WARN_DIFF_TRUNCATED = True  # Warn in prompt if diff was truncated

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

        if not cls.CURSOR_API_KEY and not cls.REVIEW_PAUSED:
            errors.append("API key is not set (CI input: openrouter-api-key / secret OPENROUTER_API_KEY)")

        if not cls.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN is not set")

        if not cls.GITHUB_REPOSITORY:
            errors.append("GITHUB_REPOSITORY is not set")

        if cls.REVIEW_LANGUAGE not in ['vietnamese', 'english']:
            errors.append(f"Invalid REVIEW_LANGUAGE: {cls.REVIEW_LANGUAGE}. Must be 'vietnamese' or 'english'")

        # Stack/API checks are unused while review is paused; skip so CI stays green.
        if cls.REVIEW_PAUSED:
            return errors

        if not cls.STACK:
            errors.append("STACK is not set")

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
        print(f"   CURSOR_API_KEY:       {'✅ SET' if cls.CURSOR_API_KEY else '❌ NOT SET'} (from openrouter-api-key)")
        print(f"   CURSOR_MODEL:         {cls.CURSOR_MODEL} (hardcoded in repo)")
        print(f"   REVIEW_PAUSED:        {cls.REVIEW_PAUSED}")
        print("=" * 60)
        print()
