#!/usr/bin/env bash
# PreToolUse hook: block Edit/Write/MultiEdit on openapi-python-client generated files.
#
# Reads Claude Code's hook payload from stdin (JSON with tool_input.file_path),
# matches against the generated-file globs from CLAUDE.md "File Rules", and exits
# with status 2 to block the call. The stderr message is shown to the agent.

set -euo pipefail

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

if [[ -z "$file_path" ]]; then
  exit 0
fi

case "$file_path" in
  */frontapp_public_api_client/api/*.py | \
  */frontapp_public_api_client/api/*/*.py | \
  */frontapp_public_api_client/models/*.py | \
  */frontapp_public_api_client/client.py | \
  */frontapp_public_api_client/client_types.py | \
  */frontapp_public_api_client/errors.py)
    cat >&2 <<EOF
STOP — "$file_path" is a generated file (openapi-python-client output).

Do not edit generated files directly. To change them, edit the source and regenerate:

  • OpenAPI spec       docs/frontapp-openapi.yaml          (vendored — never edit in place)
  • Refresh from upstream  uv run python scripts/vendor_spec.py
  • Sanitization rules  scripts/vendor_spec.py             (patch here for upstream quirks)
  • Regenerate client  uv run poe regenerate-client        (~1-2 min, NEVER cancel)

For ergonomic wrappers around generated endpoints, edit hand-written modules:
  frontapp_public_api_client/helpers/<resource>.py
  frontapp_public_api_client/domain/<resource>.py
  frontapp_public_api_client/utils.py

See CLAUDE.md → "Known Pitfalls" → "Editing generated files".
EOF
    exit 2
    ;;
esac

exit 0
