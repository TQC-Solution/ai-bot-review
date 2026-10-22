#!/usr/bin/env bash
# Cài sẵn Claude Code CLI trước khi gọi anthropics/claude-code-action.
# Lý do: action tự cài bằng `curl -fsSL https://claude.ai/install.sh | bash`, chỉ thử 3 lần cách nhau 5s.
# Khi claude.ai/CDN trả HTTP 4xx/5xx (thường là 429/403 do giới hạn tải) thì curl -f thoát mã 22
# → "Failed to install Claude Code after 3 attempts: Install failed with exit code 22".
# Script này thử lâu hơn (backoff 0/10/20/40/60s), rồi chuyển sang npm registry nếu vẫn lỗi,
# và trả đường dẫn qua output `path` để truyền vào `path_to_claude_code_executable`.
set -uo pipefail

VERSION="${CLAUDE_CODE_VERSION:-}"   # rỗng = bản stable mới nhất
BIN="$HOME/.local/bin/claude"

works() { [ -x "$1" ] && "$1" --version >/dev/null 2>&1; }
done_with() { echo "Claude Code: $1 ($("$1" --version 2>/dev/null))"; echo "path=$1" >> "$GITHUB_OUTPUT"; exit 0; }

# Runner tự host có thể đã có sẵn
if works "$BIN"; then done_with "$BIN"; fi

for delay in 0 10 20 40 60; do
  [ "$delay" -gt 0 ] && { echo "Thử lại sau ${delay}s..."; sleep "$delay"; }
  echo "::group::install.sh ${VERSION:-latest}"
  if curl -fsSL --retry 3 --retry-delay 5 https://claude.ai/install.sh | bash -s -- ${VERSION}; then
    echo "::endgroup::"
    works "$BIN" && done_with "$BIN"
  else
    echo "::endgroup::"
  fi
done

echo "::warning::install.sh lỗi liên tục, chuyển sang cài qua npm"
if command -v npm >/dev/null 2>&1; then
  for delay in 0 15 30; do
    [ "$delay" -gt 0 ] && sleep "$delay"
    if npm install -g "@anthropic-ai/claude-code${VERSION:+@$VERSION}" --no-audit --no-fund; then
      P="$(npm prefix -g)/bin/claude"
      works "$P" && done_with "$P"
    fi
  done
fi

echo "::error::Không cài được Claude Code (install.sh và npm đều lỗi)"
exit 1
