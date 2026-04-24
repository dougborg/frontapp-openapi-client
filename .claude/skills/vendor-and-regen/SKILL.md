---
name: vendor-and-regen
description: >-
  Refresh the vendored Front OpenAPI spec from upstream and regenerate the
  Python client safely. Use when pulling upstream API changes, when a new
  endpoint is needed, or when debugging codegen drift. NEVER edit the vendored
  spec or generated files directly — patch scripts/vendor_spec.py instead.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit
  - Write
  - Bash(uv run python scripts/vendor_spec.py)
  - Bash(uv run poe regenerate-client)
  - Bash(uv run poe agent-check)
  - Bash(uv run poe quick-check)
  - Bash(uv run poe check)
  - Bash(uv run poe fix)
  - Bash(uv run poe test *)
  - Bash(git status)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git add *)
  - Bash(git commit *)
---

# Vendor + Regenerate the Client

Pull upstream changes from `frontapp/front-api-specs`, sanitize them, regenerate
the Python client, and surface anything that broke.

## PURPOSE

Encode the spec-refresh workflow as a single safe motion. The pipeline has
three steps with non-obvious failure modes: generation can succeed but produce
broken Python, the spec diff can hide breaking changes, and hand-editing either
the YAML or generated files is a footgun.

## CRITICAL

- **NEVER edit `docs/frontapp-openapi.yaml` directly.** It's vendored output —
  any in-place edit is overwritten on the next refresh. If upstream introduces
  a quirk that breaks codegen, patch the sanitization pipeline in
  `scripts/vendor_spec.py` instead.
- **NEVER edit `frontapp_public_api_client/api/`,
  `frontapp_public_api_client/models/`, or `client.py`.** They're regenerated
  output. The PreToolUse hook will block the attempt with regen instructions.
- **`uv run poe regenerate-client` takes 1-2 minutes. Do not cancel.** It
  appears to hang during the full-tree codegen but is processing.
- **Review the spec diff before regenerating.** Spec changes may rename fields,
  remove endpoints, or shift response shapes — all of which can silently break
  hand-written helpers/domain code.

## ASSUMES

- Working tree is clean (or you've stashed unrelated changes).
- You're on a feature branch, not `main`.
- `uv sync --all-extras` has run recently.
- Upstream URL still points at
  `frontapp/front-api-specs` → `core-api/core-api.json` (check
  `scripts/vendor_spec.py` if the user says it moved).

## STANDARD PATH

1. **Refresh the vendored spec.**
   ```bash
   uv run python scripts/vendor_spec.py
   ```
   This downloads, sanitizes (path-param examples, binary downloads,
   `PROPERTY_DEFAULTS_TO_STRIP`, Unicode confusables), and writes
   `docs/frontapp-openapi.yaml`.

2. **Review the YAML diff** before regenerating. This is the load-bearing step.
   ```bash
   git diff docs/frontapp-openapi.yaml | less
   ```
   Look specifically for:
   - **Removed paths** — any hand-written helper that imports from that
     `api/<tag>/<module>.py` will break on regen.
   - **Renamed schema components** — `ConversationResponse` → something else
     means every `unwrap_as(response, ConversationResponse)` call breaks.
   - **Field type changes** — e.g. `created_at: integer` → `created_at: string`
     would break the epoch-second converter in the domain projection.
   - **New required fields** on request bodies — generated function signatures
     gain a positional arg, breaking existing callers.

3. **Note any schema changes that need hand-written follow-up.** Keep a short
   list — you'll consult it after regen.

4. **Regenerate the client.** Do not cancel.
   ```bash
   uv run poe regenerate-client
   ```

5. **Run agent-check to surface new errors.**
   ```bash
   uv run poe agent-check
   ```
   Common fallout from a spec refresh:
   - **ImportError** in helpers — a generated module was renamed or removed.
     Update the import in `helpers/<resource>.py`.
   - **Type errors** in domain projections — a field's type changed; update
     the Pydantic model and any converter.
   - **Test failures** asserting old shapes — update the test fixture, do not
     update the test to match the broken behavior.

6. **Fix at the source.** No `noqa`, no `type: ignore`, no skipped tests. If
   the upstream change is genuinely incompatible, raise it with the user
   before working around it.

7. **Commit generated files separately from hand-written fixes.** Two commits:
   one labeled e.g. `chore(spec): refresh vendored OpenAPI spec`, one labeled
   `fix(client): adapt helpers to <renamed-thing>`. This keeps blame readable
   when someone bisects a future regression.

## EDGE CASES

- **Upstream introduces a new codegen quirk.** Add a rule to
  `scripts/vendor_spec.py`'s sanitization pipeline. Examples already encoded:
  `PATHS_TO_STRIP` (binary downloads), `PROPERTY_DEFAULTS_TO_STRIP` (allOf
  inheritance defaults like `CreateDraft.mode`), Unicode confusables. Do not
  hand-edit `docs/frontapp-openapi.yaml`.

- **New endpoint added with leading-underscore response field.** openapi-python-client
  renames `_results` to `field_results`, etc. When wiring a helper, verify with the
  `domain-advisor` agent or by reading the generated `api/<tag>/list_*.py`
  before assuming the field name.

- **Generated module name has an `_a_` infix or `removes_` prefix.** Spec
  summaries that begin with "Update a …" / "Removes …" produce
  `update_a_contact`, `removes_inbox_access`, etc. Always
  `ls frontapp_public_api_client/api/<tag>/` before writing the import.

- **`agent-check` typecheck fails on `api/` or `models/` files.** Those paths
  are deliberately excluded from `typecheck` (see CLAUDE.md → "typecheck skips
  generated code deliberately"). If `agent-check` is failing there, something
  about the typecheck configuration or `pyproject.toml`'s task path list has
  drifted — investigate the config, not the generated files.

- **Generated test fixtures break.** Tests should mock the httpx transport,
  not the helper methods, so they exercise the full unwrap path. If a test is
  asserting on a generated attrs model field that was renamed, update the
  fixture; do not pin to the old name.

- **The upstream URL changed.** Update `SPEC_URL` in `scripts/vendor_spec.py`.

## After

- If you patched the sanitization pipeline, mention it in the commit message
  so the next person hits a less surprising state.
- Open a PR with `/open-pr`. Reviewers should sanity-check the YAML diff in
  isolation from the regenerated tree.
