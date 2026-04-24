# ADR-002: Generate Client from OpenAPI Specification

## Status

Accepted

Date: 2026-04-24

## Context

Building an API client for Front's Core API requires:

- Coverage of 233 operations across 32 tags (conversations, messages, contacts,
  teammates, accounts, tags, inboxes, channels, rules, signatures, templates, drafts,
  analytics, knowledge base, custom fields, and more)
- ~120 data models
- Full type safety with type hints
- Both sync and async support
- Maintenance as Front's API evolves (upstream spec is actively maintained at
  [frontapp/front-api-specs](https://github.com/frontapp/front-api-specs))

Options for building the client:

1. **Hand-written client**: write all API methods and models manually
2. **Generated client**: auto-generate from OpenAPI specification
3. **Hybrid approach**: generate base, hand-write ergonomic helpers on top

Front publishes an OpenAPI 3.0.0 specification covering the entire Core API.
`openapi-python-client` is the most actively-maintained Python generator and produces
clean, idiomatic output.

## Decision

**Auto-generate the client from Front's OpenAPI specification** using
`openapi-python-client`, plus a pre-generation sanitization step that patches a few
upstream quirks that would otherwise break codegen.

Layered on top of the generated surface, hand-write **ergonomic helpers** for the
highest-value resources (`client.conversations`, etc. — see
[ADR-0011: Pydantic Domain Models](0011-pydantic-domain-models.md)).

### Generation pipeline

```
scripts/vendor_spec.py
    ↓ (download + sanitize)
docs/frontapp-openapi.yaml
    ↓ (openapi-python-client)
frontapp_public_api_client/{api,models,client,…}/  [generated]
    +
frontapp_public_api_client/{frontapp_client,helpers,domain,utils}.py  [hand-written]
```

### Vendor-time sanitization

`scripts/vendor_spec.py` downloads
`https://raw.githubusercontent.com/frontapp/front-api-specs/main/core-api/core-api.json`
and applies three patches before writing `docs/frontapp-openapi.yaml`:

1. **Strip `example` keys from path parameters.** openapi-python-client renders
   `example` values as Python default arguments, which breaks signatures where a
   required path param has an example and is followed by a required param without one —
   e.g. `def f(article_id='kba_123', attachment_id)` is invalid Python.

2. **Drop binary attachment-download paths.** Endpoints returning `*/*` binary content
   (`/messages/{id}/download/{attachment_link_id}`, etc.) can't be modeled cleanly by
   openapi-python-client. If we need attachment downloads we'll hand-wire them on the
   client.

3. **Drop inherited defaults that break allOf merges.** `CreateDraft.mode` has
   `default: "private"`; `EditDraft` is an allOf over `ReplyDraft` that narrows the enum
   to `["shared"]`. The generator emits `EditDraftMode.PRIVATE` as the default, which
   references an unimported enum and violates the narrowed schema.

When upstream adds a new quirk that breaks codegen, extend `scripts/vendor_spec.py`
rather than hand-editing the vendored YAML — the vendoring step is the source of truth
for spec modifications.

### Generated vs. hand-written boundary

```
frontapp_public_api_client/
├── api/              # 32 tag modules, 233 operations (generated)
├── models/           # ~120 attrs request/response models (generated)
├── client.py         # Base client + AuthenticatedClient (generated)
├── client_types.py   # UNSET, Response, Unset, File (generated)
├── errors.py         # Generator error types (generated)
├── frontapp_client.py  # Enhanced client (hand-written)
├── helpers/          # client.conversations, future helpers (hand-written)
├── domain/           # Pydantic domain models (hand-written)
├── utils.py          # unwrap/is_success/exceptions (hand-written)
└── api_wrapper/      # Resource + registry scaffolding (hand-written)
```

Clear separation:

- **Generated code** (`api/`, `models/`, `client.py`, `client_types.py`, `errors.py`):
  never edit manually; regenerated from the spec
- **Hand-written code** (`frontapp_client.py`, `helpers/`, `domain/`, `utils.py`,
  `api_wrapper/`): hand-maintained enhancements

## Consequences

### Positive

1. **Always in sync**: regenerate from upstream spec to get new endpoints
2. **Type safety**: full type hints for all 120+ models and 233 operations
3. **Completeness**: 100% endpoint coverage guaranteed
4. **Maintainability**: one script (`regenerate_client.py`) covers the full regeneration
   flow
5. **Reliability**: openapi-python-client is well-tested and actively maintained
6. **Both sync and async**: generator creates both variants automatically
7. **IDE support**: full autocomplete and type checking
8. **Zero manual boilerplate**: 233 endpoint modules auto-created

### Negative

1. **Generator dependency**: subject to `openapi-python-client` updates
2. **Generated code style**: limited control over the emitted output
3. **Breaking changes**: Front spec changes can break the generated client
4. **Learning curve**: need to understand the generator's naming conventions (notably
   the `field_` prefix for `_`-prefixed fields — `_results` becomes `field_results`)
5. **Large codebase**: tens of thousands of lines of generated code
6. **Upstream quirks**: a few Front spec patterns need sanitization at vendor time (see
   above); bug reports upstream have varying response times

### Neutral

1. **Spec maintenance**: pin a known-good commit SHA of `frontapp/front-api-specs` if
   upstream breaks us; otherwise re-vendor on demand
2. **Generation time**: ~1-2 minutes to regenerate the full client
3. **Build dependencies**: requires `npx` for Redocly validation (advisory only in this
   repo — see `scripts/regenerate_client.py`)

## Alternatives considered

### Hand-written client

Write all 233 operations and 120 models manually.

**Pros**: full control over implementation; custom patterns and conventions; no
generator dependency; simpler debugging.

**Cons**: massive manual effort; error-prone typing of 120 models; hard to keep in sync
with Front's API evolution; no guarantee of completeness; months of initial development.

**Rejected**: too much manual work for no material benefit on top of what the generator
produces.

### Minimal client + manual additions

Generate a minimal base client, write wrappers for each endpoint.

**Pros**: some automation; can customize wrappers; type safety from generation.

**Cons**: still requires manual wrappers for every endpoint; wrappers break on Front API
changes; duplication between generated and wrapper code.

**Rejected**: the hybrid pattern we actually use (generated raw + hand-written helpers
for key resources) gets the same benefits without wrapping every endpoint. See
[ADR-0011: Pydantic Domain Models](0011-pydantic-domain-models.md) for the helper layer.

### Different generator

Use alternative OpenAPI generators (`openapi-generator`, `datamodel-code-generator`,
custom generator).

**Pros**: might have different features; more customization options.

**Cons**: `openapi-python-client` is best-of-breed for Python; OpenAPI-3-native;
produces idiomatic Python; active community; already handles 95%+ of Front's spec
without intervention.

**Rejected**: `openapi-python-client` is the best Python generator available. The few
quirks we hit are easier to patch in `scripts/vendor_spec.py` than to fix by switching
tools.

## Implementation details

### Regeneration process

```bash
# Refresh the vendored spec from upstream
uv run python scripts/vendor_spec.py

# Regenerate the client from the vendored spec
uv run poe regenerate-client
```

The `scripts/regenerate_client.py` script:

1. Validates the spec with `openapi-spec-validator`
2. Runs Redocly lint (advisory — Front's spec has style issues we can't fix upstream, so
   Redocly is non-fatal)
3. Runs `openapi-python-client` against `openapi-python-client-config.yml`
4. Auto-fixes generated code with `ruff check --fix --unsafe-fixes`
5. Moves generated code into `frontapp_public_api_client/`
6. Runs test suite

### Code-quality automation

The regeneration automatically fixes:

- Import sorting and unused imports
- Code style consistency
- Line length and formatting
- Type hint standardization

No manual patches to generated code are needed.

### Maintaining custom code

Custom enhancements live in clearly-separated files that the regeneration never touches:

- `frontapp_client.py` — resilient client entry point
- `helpers/*.py` — ergonomic facades (`client.conversations`, etc.)
- `domain/*.py` — Pydantic domain models
- `utils.py` — `unwrap` / `is_success` / error types
- `api_wrapper/*.py` — generic `Resource` + `RESOURCE_REGISTRY`

## References

- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
- [OpenAPI 3.0.0 Specification](https://spec.openapis.org/oas/v3.0.0)
- [Front Developer Portal](https://dev.frontapp.com/reference/introduction)
- [frontapp/front-api-specs](https://github.com/frontapp/front-api-specs) — upstream
  OpenAPI spec
- [`scripts/vendor_spec.py`](../../../scripts/vendor_spec.py) — upstream download +
  sanitization
- [`scripts/regenerate_client.py`](../../../scripts/regenerate_client.py) — generator
  driver
- [`docs/frontapp-openapi.yaml`](../../../docs/frontapp-openapi.yaml) — vendored spec
