#!/usr/bin/env bash
# Single source of truth for generated/vendored file globs.
#
# Sourced by .claude/hooks/block-generated-edits.sh (defense PreToolUse) and
# .claude/hooks/format-on-edit.sh (no-op skip in PostToolUse). Adding a new
# generated path means changing it once, here.
#
# Keep in sync with the "GENERATED — DO NOT EDIT" row of CLAUDE.md → File Rules.
# CI itself doesn't enforce sync — the prose row is for humans, this list is
# for hooks — but a stale CLAUDE.md row drifting from this list is the exact
# problem this consolidation prevents going forward.

# is_generated_path PATH
# Returns 0 if PATH matches a generated or vendored file, 1 otherwise.
is_generated_path() {
  case "$1" in
    */frontapp_public_api_client/api/*.py | \
    */frontapp_public_api_client/api/*/*.py | \
    */frontapp_public_api_client/models/*.py | \
    */frontapp_public_api_client/client.py | \
    */frontapp_public_api_client/client_types.py | \
    */frontapp_public_api_client/errors.py | \
    */docs/frontapp-openapi.yaml | \
    */docs/api-facts.yaml | \
    */packages/frontapp-client/src/generated/* | \
    */packages/frontapp-client/src/generated/*/*)
      return 0
      ;;
  esac
  return 1
}
