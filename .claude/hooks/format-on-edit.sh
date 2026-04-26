#!/usr/bin/env bash
# PostToolUse hook: silently format files after Edit/Write/MultiEdit succeeds.
#
# - *.py  → ruff check --fix && ruff format (one `uv run` to amortize startup)
# - *.md  → pnpm exec prettier --write
#
# Zero-token on success. Never blocks (exit 0 even when the formatter exits
# non-zero) — formatting failures must not undo a successful edit. PostToolUse
# fires after the edit is already on disk, so silently skipping a malformed
# payload is the right call here (unlike the PreToolUse defense hook).

set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib/generated-paths.sh
source "${script_dir}/_lib/generated-paths.sh"

input=$(cat)

file_path=$(python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
print((data.get("tool_input") or {}).get("file_path") or "")
' <<<"$input")

# Cheap extension check first — most edits are non-py/md (json/yaml/toml/etc.)
# and bailing here avoids forking python a second time and stat-ing the file.
case "$file_path" in
  *.py | *.md) ;;
  *) exit 0 ;;
esac

if [[ -z "$file_path" || ! -f "$file_path" ]]; then
  exit 0
fi

# Don't try to format generated/vendored output (edits there are blocked
# by block-generated-edits.sh anyway; defense in depth).
if is_generated_path "$file_path"; then
  exit 0
fi

# Build/cache directories — never format these (large, and not source).
case "$file_path" in
  */node_modules/* | \
    */.venv/* | \
    */dist/* | \
    */build/*)
    exit 0
    ;;
esac

# CLAUDE_PROJECT_DIR is set by Claude Code; without it we can't reliably find
# the project root for uv/pnpm config discovery, so skip rather than guess.
if [[ -z "${CLAUDE_PROJECT_DIR:-}" ]]; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR" || exit 0

case "$file_path" in
  *.py)
    if command -v uv >/dev/null 2>&1; then
      # One `uv run` invocation for both — amortizes uv's setup cost
      # (~150-300ms) so a typical .py edit takes ~half as long.
      uv run sh -c 'ruff check --fix "$1" && ruff format "$1"' _ "$file_path" \
        >/dev/null 2>&1 || true
    fi
    ;;
  *.md)
    if command -v pnpm >/dev/null 2>&1; then
      pnpm exec prettier --write --log-level=silent "$file_path" \
        >/dev/null 2>&1 || true
    fi
    ;;
esac

exit 0
