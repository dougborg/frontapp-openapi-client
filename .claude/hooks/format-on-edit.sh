#!/usr/bin/env bash
# PostToolUse hook: silently format files after Edit/Write/MultiEdit succeeds.
#
# - *.py    → uv run ruff format && uv run ruff check --fix
# - *.md    → pnpm exec prettier --write
#
# Stays zero-token on success (>/dev/null). Reports to stderr only on hard
# failures, and never blocks (exit 0 even when the formatter exits non-zero).
# Skips files that do not exist (edit was blocked or rolled back) and files
# under generated/vendored directories.

set -uo pipefail

input=$(cat)

file_path=$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
tool_input = data.get("tool_input") or {}
print(tool_input.get("file_path") or "")
')

if [[ -z "$file_path" || ! -f "$file_path" ]]; then
  exit 0
fi

# Don't try to format generated/vendored output (edits there are blocked
# anyway by block-generated-edits.sh; this is defensive).
case "$file_path" in
  */frontapp_public_api_client/api/*|\
  */frontapp_public_api_client/models/*|\
  */frontapp_public_api_client/client.py|\
  */frontapp_public_api_client/client_types.py|\
  */frontapp_public_api_client/errors.py|\
  */docs/frontapp-openapi.yaml|\
  */node_modules/*|\
  */.venv/*|\
  */dist/*|\
  */build/*)
    exit 0
    ;;
esac

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$file_path")}" || exit 0

case "$file_path" in
  *.py)
    if command -v uv >/dev/null 2>&1; then
      uv run ruff format "$file_path" >/dev/null 2>&1 || true
      uv run ruff check --fix "$file_path" >/dev/null 2>&1 || true
    fi
    ;;
  *.md)
    if command -v pnpm >/dev/null 2>&1; then
      pnpm exec prettier --write --log-level=silent "$file_path" >/dev/null 2>&1 || true
    fi
    ;;
esac

exit 0
