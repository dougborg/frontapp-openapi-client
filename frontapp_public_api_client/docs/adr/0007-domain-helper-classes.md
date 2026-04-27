# ADR-0007: Domain Helper Classes

## Status

Accepted

Date: 2026-04-26

## Context

The generated API surface — `from frontapp_public_api_client.api.<tag> import <op>` —
exposes every endpoint Front's spec defines. It is direct, type-safe, and complete, but
the per-call boilerplate adds up:

```python
from frontapp_public_api_client.api.conversations import list_conversations
from frontapp_public_api_client.models.list_conversations_sort_order import (
    ListConversationsSortOrder,
)
from frontapp_public_api_client.utils import unwrap

response = await list_conversations.asyncio_detailed(
    client=client,
    q="status:open tag:urgent",
    limit=50,
    sort_order=ListConversationsSortOrder("desc"),
)
parsed = unwrap(response)
results = getattr(parsed, "field_results", None) or []
convs = [Conversation.model_validate(c.to_dict()) for c in results]
```

Every caller repeats five steps:

1. Import the generated endpoint module
2. Import any enum models for typed parameters
3. Call `asyncio_detailed`
4. Unwrap the response and dig out `field_results` (the `_results` → `field_results`
   rename is a documented Known Pitfall)
5. Project attrs models into Pydantic domain models (ADR-0011) for business code

The same five steps repeat across MCP tools, scripts, application code. Multiplying that
over ~30 resources and several methods per resource produces a lot of duplicated wiring.

The auto-pagination cursor walk is even more boilerplate: each iterator implementation
needs to extract the next-page token from `_pagination.next`, feed it back into the next
call, terminate on empty pages, and respect `max_pages` / `max_items` caps.

## Decision

Provide **hand-written ergonomic facades** in `frontapp_public_api_client.helpers.*`,
exposed as lazy properties on `FrontappClient`:

```python
async with FrontappClient() as client:
    convs = await client.conversations.list(q="status:open tag:urgent", limit=50)
    async for conv in client.conversations.iter_all(q="status:open"):
        ...
```

The shape:

- **One module per resource** — `helpers/conversations.py`, `helpers/contacts.py`,
  `helpers/drafts.py`, `helpers/messages.py`, `helpers/tags.py`, `helpers/inboxes.py`,
  `helpers/teammates.py`. New verticals add a sibling module.
- **Class inherits from `Base`** — defined in `helpers/base.py`. `Base.__init__` stores
  the `FrontappClient`; `Base._paginate` walks Front's cursor pagination so each
  helper's `iter_*` methods are a thin wrapper.
- **Lazy property on `FrontappClient`** — `client.conversations` instantiates
  `Conversations(self)` on first access and caches it. New verticals add a property next
  to the existing ones.
- **Method-level imports** — generated endpoint modules and enum models are imported
  inside each method, not at module top-level. Keeps
  `from frontapp_public_api_client import FrontappClient` fast and avoids dragging the
  entire `api/` tree into every caller's import graph.
- **Returns Pydantic domain models** — list/get methods project attrs through
  `Conversation.model_validate(item.to_dict())` (see ADR-0011). Mutations return the
  fresh domain model after the call.
- **Naming mirrors Front, not the spec quirks** — `client.contacts.update(...)` even
  though the generated module is `update_a_contact` (the `_a_` infix is openapi-python-
  client's handling of "Update a contact" summaries). Helper names hide the quirk.

### The canonical template

`helpers/conversations.py` is the canonical template — when scaffolding a new vertical,
mirror its structure:

```python
class Conversations(Base):
    """Ergonomic operations over Frontapp's ``/conversations*`` endpoints."""

    async def list(self, *, q=None, limit=None, page_token=None, ...) -> list[Conversation]:
        from frontapp_public_api_client.api.conversations import list_conversations
        from frontapp_public_api_client.domain import Conversation
        from frontapp_public_api_client.utils import unwrap

        response = await list_conversations.asyncio_detailed(
            client=self._client, q=q, limit=limit, page_token=page_token, ...
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Conversation.model_validate(c.to_dict()) for c in results]

    async def iter_all(self, *, q=None, limit=None, ...) -> AsyncIterator[Conversation]:
        from frontapp_public_api_client.api.conversations import list_conversations
        from frontapp_public_api_client.domain import Conversation

        async for conv in self._paginate(
            list_conversations.asyncio_detailed,
            projector=lambda item: Conversation.model_validate(item.to_dict()),
            q=q, limit=limit,
        ):
            yield conv
```

### Why classes, not modules of free functions

Three reasons the helpers are classes (with `Base.__init__` storing the client) rather
than free functions taking a `FrontappClient` argument:

1. **Bound client** — `client.conversations.list(...)` reads cleaner than
   `conversations.list(client, ...)`, and the bound shape mirrors how the underlying
   resource is structured ("operations on conversations" → a Conversations object).
2. **Shared pagination machinery** — `Base._paginate` is genuinely shared state-aware
   logic (max_pages defaults from the client, debug logging via `self._client.logger`).
   Inheriting it is cheaper than passing it around.
3. **Lazy property registration** — the `FrontappClient.<resource>` property pattern
   needs an instance to attach to. A class is the natural target.

## Consequences

### Positive

1. **Boilerplate elimination** — five steps collapse to one method call.
2. **Discoverability** — IDE autocomplete on `client.` reveals every vertical at once.
3. **Single canonical pattern** — the `Base` + lazy-property + `Helpers(Base)` shape is
   stereotyped enough that a new vertical is a search-and-replace exercise. The
   `/new-vertical` skill (`.claude/skills/new-vertical/`) and `vertical-planner` agent
   (`.claude/agents/vertical-planner.md`) encode this.
4. **Domain-model projection happens at the boundary** — every helper returns Pydantic
   domain models, never raw attrs. Callers don't need `unwrap_unset` or `to_dict()`.
5. **Method-level imports keep the package light** — `import FrontappClient` does not
   transitively import every generated endpoint module.
6. **`field_results` gotcha is hidden** — every helper's list method does the
   `getattr(parsed, "field_results", None) or []` dance once; callers never see it.
7. **Cursor pagination is one line** — `iter_all` is a thin wrapper around
   `Base._paginate`; the next-token extraction and termination logic is shared.

### Negative

1. **Two API layers to know about** — generated `api/<tag>` access is still available
   for endpoints we haven't wrapped, so the client has both a direct-access surface and
   a helper surface. Document which one to reach for in `guide.md` (helpers first;
   direct access for unwrapped endpoints).
2. **Duplication risk** — every helper repeats the same import-and-unwrap shape. If we
   ever change the unwrap convention (e.g. moving from `unwrap` to a different helper),
   every method needs an edit. Mitigated by the `vertical-planner` plan-before-code
   workflow and the canonical-template reference.
3. **Hand-written, so it lags spec changes** — when Front adds a new endpoint, the
   helper layer doesn't pick it up automatically; someone has to file a vertical issue
   and ship it. Acceptable: the helper layer is selectively curated, not exhaustive.

### Neutral

1. **Hand-written code is in the typecheck task scope** — `helpers/` is included in
   `uv run poe typecheck`'s path list, unlike the generated `api/` and `models/` trees
   which are excluded (issue #8). Helper changes get the full type-check rigor.
2. **Mutations need a return-value decision per resource** — most return the fresh
   domain model after the call; some (delete, archive) return `None`. No global rule —
   the canonical template shows the common cases.
3. **Two-step confirm lives in the MCP layer, not here** — the helper layer is the
   ergonomic Python surface; the MCP layer adds confirm-before-execute for agent safety
   (see ADR-0010). Helpers themselves don't gate.

## Alternatives considered

### Free functions taking a client argument

```python
from frontapp_public_api_client.helpers.conversations import list_conversations

convs = await list_conversations(client, q="status:open")
```

**Rejected**: loses bound-client ergonomics and IDE autocomplete-on-`client.`
discoverability. Forces callers to import every helper module separately.

### Mixin into `FrontappClient`

```python
client = FrontappClient()
await client.list_conversations(q="status:open")
```

**Rejected**: explodes the client's namespace (~50 methods across ~30 verticals). Loses
the resource grouping that `client.conversations.list()` makes obvious. Makes the client
class hard to read.

### Module-level helpers without classes (free functions in `helpers/conversations.py`)

A class-free version of the helper modules: `helpers/conversations.py` exports
`async def list(client, ...)`, etc.

**Rejected**: doesn't compose cleanly with the lazy-property pattern (no instance for
the property to return), can't share `_paginate` without passing the client into every
call, and reads worse at the call site.

### Code-generate helpers from the spec

Auto-generate the helper layer from `docs/frontapp-openapi.yaml` with a separate codegen
pass.

**Rejected — for now**: the helper layer is intentionally selective (it doesn't wrap
every endpoint, only the high-traffic ones), and the projection-to-domain-model step is
a judgment call that doesn't generate cleanly. Revisit if the matrix of wrapped
endpoints grows large enough that hand-writing becomes the bottleneck.

## Implementation notes

### Adding a new helper vertical

The full sequence is encoded in the `/new-vertical` skill. Briefly:

1. Run the `vertical-planner` agent to produce a plan that confirms generated module
   names and list-response shapes (the `field_results` vs raw-array question is
   pre-computed in `docs/api-facts.yaml`).
2. Create `frontapp_public_api_client/domain/<resource>.py` (Pydantic projections,
   ADR-0011).
3. Create `frontapp_public_api_client/helpers/<resource>.py` (`class Resource(Base)`).
4. Add a lazy property to `FrontappClient` and a `TYPE_CHECKING` import.
5. Add the helper class to `helpers/__init__.py` `__all__`.
6. Wire the MCP tool module (ADR-0010) and update `resources/help.py`.
7. Tests + README coverage table.

### Cross-vertical sub-resources

Some helpers span multiple generated tags. `client.contacts` covers the `contacts/`,
`contact_handles/`, and `contact_notes/` tags as one logical resource — sub-resource
methods (`add_handle`, `delete_handle`, `add_note`, `list_notes`) live on the same
`Contacts` class. Mirror this when a new vertical's endpoints are split across spec
tags.

### `iter_*` variants

Every list method has a sibling `iter_*` that walks pages automatically via
`Base._paginate`. The `iter_*` form is the auto-pagination async iterator from ADR-003 —
preferred when iterating every match in a query, since the cursor plumbing and
termination logic stay hidden.

## References

- [`helpers/base.py`](https://github.com/dougborg/frontapp-openapi-client/blob/main/frontapp_public_api_client/helpers/base.py)
  — `Base` class with `_paginate`
- [`helpers/conversations.py`](https://github.com/dougborg/frontapp-openapi-client/blob/main/frontapp_public_api_client/helpers/conversations.py)
  — canonical template
- [ADR-002: Generate Client from OpenAPI Specification](0002-openapi-code-generation.md)
  — the layer this sits on top of
- [ADR-003: Transparent Automatic Pagination](0003-transparent-pagination.md) — the
  pagination model that `Base._paginate` implements
- [ADR-006: Utility Functions for Response Unwrapping](0006-response-unwrapping-utilities.md)
  — the `unwrap` / `unwrap_as` helpers used internally
- [ADR-008: Avoid Traditional Builder Pattern](0008-avoid-builder-pattern.md) — why
  helpers are direct method calls, not fluent chains
- [ADR-0011: Pydantic Domain Models for Business Entities](0011-pydantic-domain-models.md)
  — what helpers return
- [`docs/api-facts.yaml`](https://github.com/dougborg/frontapp-openapi-client/blob/main/docs/api-facts.yaml)
  — facts file the `vertical-planner` agent and humans consult before writing a helper
