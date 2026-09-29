"""AI Code Reviewer Package for code projects using Cursor Agent SDK."""

__version__ = "5.0.0"

from .config import Config
from .github_client import GitHubClient, GitHubAPIError
from .cursor_client import CursorClient, CursorAPIError
from .prompt_builder import PromptBuilder
from .diff_chunker import DiffChunker, DiffChunk
from .utils import (
    get_pr_number_from_ref,
    format_validation_errors,
    create_fallback_comment,
    create_paused_comment,
    print_usage_instructions
)

__all__ = [
    "Config",
    "GitHubClient",
    "GitHubAPIError",
    "CursorClient",
    "CursorAPIError",
    "PromptBuilder",
    "DiffChunker",
    "DiffChunk",
    "get_pr_number_from_ref",
    "format_validation_errors",
    "create_fallback_comment",
    "create_paused_comment",
    "print_usage_instructions",
]
