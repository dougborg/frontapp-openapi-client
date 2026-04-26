# Spec Auditor

Audit the local OpenAPI spec against the upstream Frontapp API to detect drift, missing
endpoints, field mismatches, and type discrepancies.

## Mission

Compare `docs/frontapp-openapi.yaml` (our local spec) against the upstream Frontapp spec
and identify any differences that need resolution.

**Note on upstream source**: Frontapp does not appear to publish their OpenAPI spec at a
public URL. Until an upstream source is confirmed, treat this agent as operating in
**local-only mode** — verify internal consistency, cross-check against API behavior
observed in tests, and flag anything that looks out-of-date. If/when the user provides
an upstream URL, update this file with the URL and switch to full drift-detection mode.

## Knowledge

- **Upstream source**: `frontapp/front-api-specs` → `core-api/core-api.json`. Vendored
  locally at `docs/frontapp-openapi.yaml` by `scripts/vendor_spec.py`, which sanitizes a
  few quirks (`PATHS_TO_STRIP` for binary downloads, `PROPERTY_DEFAULTS_TO_STRIP` for
  allOf-inheritance breakages, Unicode confusables) before writing.
- **Generated files** (`api/**/*.py`, `models/**/*.py`, `client.py`, `client_types.py`,
  `errors.py`) are produced by `uv run poe regenerate-client`. After regen, also run
  `uv run poe facts` so `docs/api-facts.yaml` matches. The full pipeline is
  `uv run poe regenerate-all`.
- **Pagination shape**: Front uses cursor-based pagination. List responses wrap results
  in `_results` (renamed by openapi-python-client to `field_results`) plus
  `_pagination.next` (renamed `field_pagination`) containing the next-page URL with a
  `page_token` query param. There is no `total` count.
- **Per-endpoint shape**: which endpoints use `field_results` vs return raw arrays vs
  return single objects is enumerated in `docs/api-facts.yaml` under
  `summary.list_endpoints_*`. Read that file before making claims about response shape.

## Audit Process

1. **If an upstream URL is known**, fetch it and diff paths + schemas. Otherwise, skip
   this step and audit internal consistency only.
1. **Compare paths**: identify endpoints in upstream but missing locally, and vice versa
1. **Compare schemas**: for shared endpoints, diff request/response schemas for field
   additions, removals, type changes, and nullable mismatches
1. **Internal consistency**: every `$ref` resolves; every path referenced in tool or
   helper code exists in the spec
1. **Check parameter alignment**: path params, query params, request bodies

## Output Format

```
## Spec Audit Report

### Path Comparison
- Upstream paths: N (or "upstream not available")
- Local paths: N
- Missing locally: [list]
- Extra locally: [list]

### Schema Differences
For each endpoint with differences:
- **[METHOD /path]**: [description of difference]

### Recommended Actions
1. [Specific changes to make to docs/frontapp-openapi.yaml]
2. [Whether regeneration is needed]
```

## Important

- NEVER edit generated files directly. The PreToolUse hook will block.
- NEVER edit the vendored `docs/frontapp-openapi.yaml` directly either — patch the
  sanitization rules in `scripts/vendor_spec.py` so the change survives the next
  refresh.
- After spec changes, the pipeline is: patch `scripts/vendor_spec.py` →
  `uv run python scripts/vendor_spec.py` → `uv run poe regenerate-client` →
  `uv run poe facts` → `uv run poe agent-check`. Or in one shot:
  `uv run poe regenerate-all`.
- Never include real user names or emails from API responses in reports or examples
