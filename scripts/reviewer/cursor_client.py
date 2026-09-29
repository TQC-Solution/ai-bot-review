"""Cursor SDK / CLI client for code review generation.

CI still passes the key via openrouter-api-key; the value must be a Cursor API key.

Primary: Cursor Cloud Agents (needs storage enabled in Cursor settings).
Fallback: Cursor CLI (`agent -p`) — local Python SDK is skipped because it
fails on GitHub Actions with RUNNING → ERROR and an empty conversation.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import asdict, is_dataclass

from cursor_sdk import (
    Agent,
    AuthenticationError,
    CloudAgentOptions,
    Cursor,
    CursorAgentError,
    RateLimitError,
)

try:
    from cursor_sdk import ConfigurationError
except ImportError:
    class ConfigurationError(CursorAgentError):  # type: ignore[no-redef]
        """Fallback if this SDK version does not export ConfigurationError."""
        pass

from .config import Config


class CursorAPIError(Exception):
    """Custom exception for Cursor SDK / API errors."""
    pass


_REVIEW_PREFIX = (
    "You are a code reviewer. Do not modify files, do not run git write commands, "
    "and do not create commits. Reply with the review markdown only.\n\n"
)


class CursorClient:
    """Client for generating reviews via the Cursor Agent SDK."""

    def __init__(self, api_key: str, project_name: str = "AI Code Review Bot", pr_number: int | None = None):
        """Initialize Cursor client.

        Args:
            api_key: Cursor API key (passed from CI as openrouter-api-key)
            project_name: Name of the project being reviewed (for logs)
            pr_number: Pull request number (for logs)

        Raises:
            CursorAPIError: If API key is not set
        """
        if not api_key:
            raise CursorAPIError("CURSOR_API_KEY not set")

        self.api_key = api_key.strip()
        self.project_name = project_name
        self.pr_number = pr_number
        self.cwd = os.getenv("GITHUB_WORKSPACE") or os.getcwd()

    def generate_review(self, prompt: str) -> str:
        """Generate code review using a Cursor agent.

        Args:
            prompt: The review prompt including code diff

        Returns:
            Generated review text

        Raises:
            CursorAPIError: If the SDK call fails
        """
        model_name = self._resolve_model(Config.CURSOR_MODEL)

        try:
            review = self._try_model_with_retry(model_name, prompt)
            if review:
                return review
            raise CursorAPIError(f"Model {model_name} returned empty response")
        except Exception as e:
            raise self._create_detailed_error(e)

    def _list_model_ids(self) -> list[str]:
        """Return model IDs available to this API key."""
        models = Cursor.models.list(api_key=self.api_key)
        ids: list[str] = []
        for model in models:
            model_id = getattr(model, "id", None)
            if model_id:
                ids.append(str(model_id))
        return ids

    def _resolve_model(self, requested: str) -> str:
        """Fail fast if the hardcoded model is not in the API-key catalog."""
        try:
            available = self._list_model_ids()
        except Exception as e:
            print(f"   ⚠️  Could not list Cursor models: {e}")
            return requested

        print(f"   Available Cursor models: {', '.join(available) or '(none)'}")

        if requested in available:
            return requested

        close = [mid for mid in available if requested in mid or mid in requested]
        hint = f" Close matches: {', '.join(close)}." if close else ""
        raise CursorAPIError(
            f"Model '{requested}' is not available for this Cursor API key.{hint}\n"
            f"   Available: {', '.join(available) or '(none)'}\n"
            f"   Fix: Team Settings → Models, enable Claude Sonnet 5 for API/SDK, "
            f"or change CURSOR_MODEL in scripts/reviewer/config.py"
        )

    def _try_model_with_retry(self, model_name: str, prompt: str) -> str | None:
        """Run the agent with retry on rate limits and retryable errors."""
        retry_delay = Config.INITIAL_RETRY_DELAY
        full_prompt = _REVIEW_PREFIX + prompt

        for attempt in range(Config.MAX_RETRIES + 1):
            try:
                if attempt > 0:
                    print(f"      Retry attempt {attempt}/{Config.MAX_RETRIES} "
                          f"after {retry_delay}s...")
                    time.sleep(retry_delay)

                print(f"   Using Cursor model: {model_name}")
                content = (self._run_agent(model_name, full_prompt) or "").strip()
                if not content:
                    return None

                print(f"   ✅ Review generated successfully with {model_name}")
                return content

            except RateLimitError as e:
                if attempt < Config.MAX_RETRIES:
                    retry_delay = self._retry_wait(e, retry_delay)
                    print(f"      ⚠️  Rate limit, retrying in {retry_delay}s...")
                    retry_delay *= Config.RETRY_BACKOFF_MULTIPLIER
                    continue
                raise CursorAPIError(
                    f"Rate limit exceeded after {Config.MAX_RETRIES} retries: {e.message}"
                ) from e

            except AuthenticationError as e:
                raise CursorAPIError(
                    "Invalid Cursor API key. "
                    "Get a key at: https://cursor.com/dashboard/api "
                    "and put it in GitHub Secret OPENROUTER_API_KEY."
                ) from e

            except ConfigurationError as e:
                raise CursorAPIError(
                    f"Invalid Cursor config/model: {e.message}. "
                    f"Check CURSOR_MODEL and Team Settings → Models."
                ) from e

            except CursorAgentError as e:
                if e.is_retryable and attempt < Config.MAX_RETRIES:
                    retry_delay = self._retry_wait(e, retry_delay)
                    print(f"      ⚠️  Retryable Cursor error ({e.code}), retrying in {retry_delay}s...")
                    retry_delay *= Config.RETRY_BACKOFF_MULTIPLIER
                    continue
                raise CursorAPIError(
                    f"Cursor SDK error: {e.message} (code={e.code}, retryable={e.is_retryable})"
                ) from e

            except CursorAPIError:
                raise

            except Exception as e:
                raise CursorAPIError(f"Unexpected error: {e}") from e

        return None

    def _run_agent(self, model_name: str, prompt: str) -> str:
        """Try cloud first; if storage is disabled, use Cursor CLI."""
        try:
            print("   Runtime: cloud (no-repo)")
            return self._run_with_options(
                prompt,
                model_name=model_name,
                cloud=CloudAgentOptions(repos=[], skip_reviewer_request=True),
            )
        except CursorAPIError:
            raise
        except Exception as cloud_error:
            cloud_text = str(cloud_error)
            print(f"   ⚠️  Cloud run failed ({cloud_text})")
            if self._is_storage_disabled_error(cloud_text):
                print(
                    "   Cursor Cloud Agents need storage enabled "
                    "(Dashboard → Cloud Agents, tắt Legacy Privacy Mode)."
                )
            print("   Falling back to Cursor CLI (agent -p)...")
            return self._run_via_cli(model_name, prompt)

    def _is_storage_disabled_error(self, message: str) -> bool:
        lowered = message.lower()
        return "storage mode is disabled" in lowered or "feature_unavailable" in lowered

    def _find_cli_binary(self) -> str | None:
        """Locate `agent` or `cursor-agent` on PATH."""
        for name in ("agent", "cursor-agent"):
            path = shutil.which(name)
            if path:
                return path
        home = os.path.expanduser("~")
        for candidate in (
            os.path.join(home, ".local", "bin", "agent"),
            os.path.join(home, ".cursor", "bin", "agent"),
            os.path.join(home, ".local", "bin", "cursor-agent"),
            os.path.join(home, ".cursor", "bin", "cursor-agent"),
        ):
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
        return None

    def _run_via_cli(self, model_name: str, prompt: str) -> str:
        """Headless Cursor CLI — works in GitHub Actions without cloud storage."""
        binary = self._find_cli_binary()
        if not binary:
            raise CursorAPIError(
                "Cloud Agents failed because storage is disabled, and Cursor CLI "
                "was not found on PATH.\n"
                "   Option 1: Enable storage at https://cursor.com/dashboard/cloud-agents "
                "(switch off Legacy Privacy Mode).\n"
                "   Option 2: Ensure the action installs Cursor CLI "
                "(curl https://cursor.com/install)."
            )

        print(f"   Runtime: Cursor CLI ({binary})")
        env = os.environ.copy()
        env["CURSOR_API_KEY"] = self.api_key

        cmd = [
            binary,
            "-p",
            "--output-format",
            "text",
            "--mode",
            "ask",
            "--model",
            model_name,
            "--force",
            prompt,
        ]
        completed = self._invoke_cli(cmd, env)
        if completed.returncode != 0 and self._is_unknown_cli_flag(completed, "mode"):
            print("   CLI does not support --mode ask; retrying without it")
            cmd = [
                binary,
                "-p",
                "--output-format",
                "text",
                "--model",
                model_name,
                "--force",
                prompt,
            ]
            completed = self._invoke_cli(cmd, env)

        if completed.stderr:
            print(f"   CLI stderr:\n{completed.stderr.strip()[:4000]}")

        if completed.returncode != 0:
            raise CursorAPIError(self._format_cli_failure(completed))

        content = (completed.stdout or "").strip()
        if not content:
            raise CursorAPIError("Cursor CLI returned empty review text")
        return content

    def _invoke_cli(self, cmd: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=600,
                env=env,
                cwd=self.cwd,
            )
        except subprocess.TimeoutExpired as e:
            raise CursorAPIError("Cursor CLI timed out after 600s") from e
        except OSError as e:
            if "argument list too long" in str(e).lower() or getattr(e, "errno", None) == 7:
                raise CursorAPIError(
                    "Review prompt is too large to pass to Cursor CLI. "
                    "Reduce PR size or enable Cloud Agent storage."
                ) from e
            raise

    def _format_cli_failure(self, completed: subprocess.CompletedProcess[str]) -> str:
        """Turn CLI stderr into an actionable error."""
        output = (completed.stderr or completed.stdout or "no output").strip()
        lowered = output.lower()
        if "weekly usage limit" in lowered or "usage limit reached" in lowered:
            return (
                "Cursor weekly usage limit reached for this API key.\n"
                "   Bot/CI đã chạy đúng; tài khoản Cursor hết hạn mức tuần.\n"
                "   Xem usage: https://cursor.com/dashboard/usage\n"
                "   Cách xử lý: đợi reset, mua credits, upgrade plan, "
                "hoặc dùng API key khác còn quota.\n"
                f"   Chi tiết: {output[:1500]}"
            )
        return f"Cursor CLI exited {completed.returncode}: {output[:4000]}"

    def _is_unknown_cli_flag(self, completed: subprocess.CompletedProcess[str], flag: str) -> bool:
        text = f"{completed.stderr or ''} {completed.stdout or ''}".lower()
        return flag in text and ("unknown" in text or "unrecognized" in text or "invalid" in text)

    def _run_with_options(
        self,
        prompt: str,
        *,
        model_name: str,
        cloud: CloudAgentOptions | None = None,
        local: LocalAgentOptions | None = None,
    ) -> str:
        """Create an agent, stream status, wait, and extract review text."""
        create_kwargs: dict = {
            "model": model_name,
            "api_key": self.api_key,
        }
        if cloud is not None:
            create_kwargs["cloud"] = cloud
        if local is not None:
            create_kwargs["local"] = local

        with Agent.create(**create_kwargs) as agent:
            agent_id = getattr(agent, "agent_id", None)
            print(f"   agent_id={agent_id}")
            run = agent.send(prompt)
            print(f"   run_id={getattr(run, 'id', None)}")

            stream_notes: list[str] = []
            try:
                for message in run.messages():
                    note = self._format_stream_message(message)
                    if note:
                        print(f"      {note}")
                        stream_notes.append(note)
            except Exception as stream_error:
                print(f"      ⚠️  Stream read failed: {stream_error}")
                stream_notes.append(f"stream_error={stream_error}")

            result = run.wait()
            if getattr(result, "status", None) == "error":
                extra = ""
                if run.supports("conversation"):
                    try:
                        extra = f" conversation={run.conversation()!r}"
                    except Exception:
                        extra = ""
                raise CursorAPIError(
                    "Cursor run failed "
                    f"({self._describe_result(result)}; stream=[{'; '.join(stream_notes) or 'none'}]{extra})"
                )

            content = (getattr(result, "result", None) or "").strip()
            if content:
                return content

            # Some SDK versions put the answer on run.result instead of wait().
            return (getattr(run, "result", None) or "").strip()

    def _format_stream_message(self, message: object) -> str:
        """Compact log line for one SDK stream message."""
        msg_type = getattr(message, "type", None)
        if msg_type == "status":
            return f"[status] {getattr(message, 'status', message)}"
        if msg_type == "tool_call":
            return (
                f"[tool] {getattr(message, 'name', '?')}:"
                f" {getattr(message, 'status', '')}"
            )
        if msg_type in ("error", "system"):
            return f"[{msg_type}] {message}"
        text = getattr(message, "text", None)
        if msg_type == "thinking" and text:
            return f"[thinking] {str(text)[:200]}"
        return ""

    def _describe_result(self, result: object) -> str:
        """Dump useful fields from a failed RunResult."""
        parts: list[str] = []
        for name in (
            "id",
            "status",
            "result",
            "error",
            "duration_ms",
            "model",
            "request_id",
        ):
            if hasattr(result, name):
                value = getattr(result, name)
                if value not in (None, ""):
                    parts.append(f"{name}={value!r}")
        if is_dataclass(result) and not parts:
            try:
                parts.append(repr(asdict(result)))
            except Exception:
                parts.append(repr(result))
        return ", ".join(parts) or repr(result)

    def _retry_wait(self, error: CursorAgentError, fallback: float) -> float:
        """Honor retry_after when the SDK provides it."""
        retry_after = getattr(error, "retry_after", None)
        if not retry_after:
            return fallback
        try:
            return float(retry_after)
        except (TypeError, ValueError):
            return fallback

    def _create_detailed_error(self, error: Exception) -> CursorAPIError:
        """Create a detailed error message based on the error type."""
        if isinstance(error, CursorAPIError):
            return error

        error_msg = str(error).lower()

        if "api key" in error_msg or "401" in error_msg or "authentication" in error_msg:
            return CursorAPIError(
                "Invalid Cursor API key.\n"
                "   Get a key at: https://cursor.com/dashboard/api\n"
                "   Update GitHub Secret: Settings → Secrets → OPENROUTER_API_KEY\n"
                "   (Secret name stays OPENROUTER_API_KEY; value must be a Cursor key)"
            )
        if "storage" in error_msg or "feature_unavailable" in error_msg:
            return CursorAPIError(
                "Cursor Cloud Agents need storage enabled.\n"
                "   Open https://cursor.com/dashboard/cloud-agents\n"
                "   Turn off Legacy Privacy Mode / enable storage, then re-run CI.\n"
                f"   Error: {error}"
            )
        if "rate" in error_msg or "429" in error_msg:
            return CursorAPIError(
                f"Cursor API rate limit exceeded.\n"
                f"   Check usage at: https://cursor.com/dashboard/usage\n"
                f"   Error: {error}"
            )
        return CursorAPIError(f"Cursor API call failed: {error}")
