#!/usr/bin/env python3
"""AI reviewer script for GitHub Actions using Cursor Agent SDK.

This is the main orchestrator that coordinates all components:
- Configuration validation
- GitHub PR fetching
- Prompt building
- AI review generation
- Comment posting

For detailed implementation, see the reviewer package modules:
- config.py: Configuration and environment variables
- github_client.py: GitHub API operations
- cursor_client.py: Cursor Agent SDK integration
- prompt_builder.py: Prompt construction
- utils.py: Helper functions
"""

import sys

from reviewer.config import Config
from reviewer.github_client import GitHubClient, GitHubAPIError
from reviewer.prompt_builder import PromptBuilder
from reviewer.utils import (
    get_pr_number_from_ref,
    format_validation_errors,
    create_paused_comment,
    print_usage_instructions
)


def main():
    """Main entry point for AI code review workflow."""

    # Print environment configuration for debugging
    Config.print_debug_info()

    # Validate configuration
    validation_errors = Config.validate()
    if validation_errors:
        # Some errors are acceptable for local testing (missing GitHub ref)
        critical_errors = [e for e in validation_errors if "GITHUB_REF" not in e]
        if critical_errors:
            print(format_validation_errors(critical_errors))
            sys.exit(1)

    # Extract PR number from GitHub ref
    pr_number = get_pr_number_from_ref(Config.GITHUB_REF)
    if not pr_number:
        print_usage_instructions(Config.GITHUB_REF)
        sys.exit(0)

    # Initialize clients
    github_client = GitHubClient(Config.GITHUB_REPOSITORY, Config.GITHUB_TOKEN)

    if Config.REVIEW_PAUSED:
        _finish_paused(github_client, pr_number)
        return

    from reviewer.cursor_client import CursorClient, CursorAPIError

    cursor_client = CursorClient(
        Config.CURSOR_API_KEY,
        project_name=Config.GITHUB_REPOSITORY or "AI Code Review Bot",
        pr_number=pr_number
    )
    prompt_builder = PromptBuilder(Config.REVIEW_LANGUAGE)

    # Step 1: Fetch PR diff
    try:
        print(f"🔍 Fetching diff for PR #{pr_number}...")
        diff = github_client.fetch_pr_diff(pr_number)
    except GitHubAPIError as e:
        print(f"❌ Failed to fetch PR diff: {e}")
        sys.exit(1)

    # Step 2: Build review prompts (may be chunked for large PRs)
    print("📝 Building review prompt(s)...")
    prompt_chunks = prompt_builder.build_chunked_prompts(diff)

    # Step 3: Generate AI review for each chunk
    all_reviews = []
    for idx, (prompt, chunk) in enumerate(prompt_chunks):
        try:
            if len(prompt_chunks) > 1:
                print(f"💬 Reviewing chunk {idx + 1}/{len(prompt_chunks)} "
                      f"({len(chunk.files)} files: {', '.join(chunk.files[:3])}...)")
            else:
                print("💬 Sending prompt to Cursor...")

            review = cursor_client.generate_review(prompt)
            all_reviews.append({
                'chunk_index': idx,
                'files': chunk.files,
                'review': review
            })

        except CursorAPIError as e:
            print(f"❌ Cursor call failed for chunk {idx + 1}: {e}")

            # Token/quota issues must not fail consumer CI.
            if idx == 0:
                _finish_paused(github_client, pr_number)
                return
            print(f"   ⚠️ Skipping chunk {idx + 1}, continuing with remaining chunks...")
            continue

    # Step 4: Merge reviews if multiple chunks
    if len(all_reviews) == 0:
        print("⚠️ No reviews generated. Posting paused notice and exiting 0.")
        _finish_paused(github_client, pr_number)
        return

    if len(all_reviews) == 1:
        final_review = all_reviews[0]['review']
    else:
        print(f"🔗 Merging {len(all_reviews)} review chunks...")
        final_review = _merge_reviews(all_reviews, Config.REVIEW_LANGUAGE)

    # Step 5: Post review to PR
    try:
        print("✉️ Posting review comment(s) to PR...")
        github_client.post_review_chunked(pr_number, final_review.strip())
        print("✅ Posted AI review comment(s) successfully.")
    except GitHubAPIError as e:
        print(f"❌ Failed to post comment: {e}")
        sys.exit(1)


def _finish_paused(github_client: GitHubClient, pr_number: str) -> None:
    """Post a paused notice and leave CI green."""
    print("⏸️ AI Code Review is paused. Skipping Cursor API.")
    try:
        github_client.post_comment(
            pr_number,
            Config.COMMENT_HEADER + create_paused_comment(Config.REVIEW_LANGUAGE),
        )
        print("✅ Posted paused notice to PR.")
    except Exception as e:
        print(f"⚠️ Could not post paused comment: {e}")
    print("Exiting successfully so CI stays green.")


def _merge_reviews(reviews: list, language: str) -> str:
    """Merge multiple chunk reviews into single review.

    Args:
        reviews: List of review dicts with 'chunk_index', 'files', 'review'
        language: Review language ('vietnamese' or 'english')

    Returns:
        Merged review text
    """
    if language == "english":
        header = "## 📋 Code Review Summary\n\n"
        header += f"_This PR was reviewed in {len(reviews)} parts due to size._\n\n"
    else:
        header = "## 📋 Tổng Hợp Code Review\n\n"
        header += f"_PR này được review theo {len(reviews)} phần do kích thước lớn._\n\n"

    merged = header

    for review_data in reviews:
        chunk_idx = review_data['chunk_index']
        files = review_data['files']
        review = review_data['review']

        # Add separator between chunks
        if language == "english":
            merged += f"\n---\n\n### Part {chunk_idx + 1}: {', '.join(files[:3])}"
            if len(files) > 3:
                merged += f" and {len(files) - 3} more files"
            merged += "\n\n"
        else:
            merged += f"\n---\n\n### Phần {chunk_idx + 1}: {', '.join(files[:3])}"
            if len(files) > 3:
                merged += f" và {len(files) - 3} files khác"
            merged += "\n\n"

        merged += review.strip() + "\n"

    return merged


if __name__ == '__main__':
    main()
