#!/usr/bin/env bash
# PostToolUse hook: silently format files after Edit/Write/MultiEdit succeeds.
#
# - *.py  → ruff format (style only — NO ruff check --fix; see #50)
# - *.md  → ./node_modules/.bin/prettier --write (direct binary, skips pnpm shim)
#
# This hook is intentionally **format-only**, not lint-and-fix. Earlier
# versions ran `ruff check --fix` here too, but it caused a race where
# TYPE_CHECKING imports got pruned between an agent's two Edits (one adding
# the import, the next adding the usage) — every vertical PR hit it 3-5
# times. Linting still happens at `uv run poe check` and in CI; doing it on
# every edit was over-eager.
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
      # Format-only — NO `ruff check --fix`. See header comment + #50.
      uv run ruff format "$file_path" >/dev/null 2>&1 || true
    fi
    ;;
  *.md)
    # Direct binary skips pnpm + node-shim startup (~250-400ms saved per edit).
    # See issue #26.
    if [[ -x ./node_modules/.bin/prettier ]]; then
      ./node_modules/.bin/prettier --write --log-level=silent "$file_path" \
        >/dev/null 2>&1 || true
    fi
    ;;
esac

exit 0
