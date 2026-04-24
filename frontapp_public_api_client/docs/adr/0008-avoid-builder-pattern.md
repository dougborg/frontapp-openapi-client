# ADR-008: Avoid Traditional Builder Pattern

## Status

Accepted

Date: 2026-04-24

## Context

The raw generated API can be verbose for complex queries with many parameters:

```python
response = await list_conversations.asyncio_detailed(
    client=client,
    q="status:open tag:urgent",
    limit=100,
    page_token="ce787da…",
    sort_by="id",
    sort_order=ListConversationsSortOrder("desc"),
)
```

The **Builder pattern** is a common approach for complex object construction:

```python
query = (
    ConversationQuery(client)
    .status("open")
    .has_tag("urgent")
    .limit(100)
    .sort_by("id", "desc")
    .execute()
)
```

Question: should we implement builders on top of the generated API?

## Decision

**No builder pattern.** Instead:

1. **Keep the generated API accessible** — it's transparent and type-safe
2. **Layer hand-written helpers** (`client.conversations.list(...)`) that wrap the
   generated calls with ergonomic signatures
3. **Provide cookbook examples** for complex queries
4. **Use Front's `q=` search syntax** for filter expressiveness instead of Python-level
   DSL

Front's own search syntax (`status:open AND tag:urgent AND after:2024-01-01`) is already
a builder-like expressive layer — adding a Python-side builder on top would either
duplicate that syntax or fight it. Keeping filter logic in the `q=` string matches
Front's model and keeps Python code focused on flow, not filter composition.

### Why the direct + helpers approach works better

- ✅ **Transparent**: clear what API calls are made
- ✅ **Type-safe**: perfect IDE autocomplete on every argument
- ✅ **Debuggable**: easy to trace to the actual HTTP call
- ✅ **Matches OpenAPI**: direct mapping to the spec
- ✅ **No learning curve**: just function parameters
- ✅ **Front's own DSL**: `q=` search syntax is the expressive layer Front designed for
  this

### What builders would cost

- ❌ **Abstraction**: hides underlying API calls
- ❌ **Learning curve**: users must learn builder methods in addition to Front's search
  syntax
- ❌ **Two ways to do everything**: confusing — helpers already exist
- ❌ **Type safety challenges**: fluent chaining is hard to type across method
  boundaries
- ❌ **Maintenance**: one builder class per resource (~30 resources), and each needs to
  stay in sync with the spec

## Consequences

### Positive

1. **Simplicity**: two layers (generated + helpers), not three
2. **Transparency**: users can see the API call in the helper source
3. **Type safety**: perfect hints on every argument
4. **Debuggability**: easy to trace and reproduce
5. **Less code**: no builder classes to maintain
6. **No ambiguity**: one idiomatic way to call each endpoint
7. **Matches Front's design**: `q=` search syntax is the expressive query DSL

### Negative

1. **Verbosity**: complex queries with many kwargs can be long (mitigated by Front's
   `q=` syntax, which compresses filters)
2. **No method chaining**: can't `.where(...).order_by(...).limit(...)` (mitigated by
   helper-layer methods that accept all filters as kwargs in a single call)
3. **No client-side validation**: parameters validated by Front, not by the builder
   (mitigated by Pydantic type checks on the helper signatures)

### Neutral

1. **Helpers cover the ergonomics gap**: `client.conversations.list(q=...)` is the
   primary user-facing API for the common case
2. **Raw access is always available**: power users can call the generated
   `list_conversations.asyncio_detailed(...)` directly

## Detailed analysis

### What builders would look like

```python
# Hypothetical fluent API
convs = await (
    ConversationQuery(client)
    .status("open")
    .tag("urgent")
    .before(datetime(2026, 3, 1))
    .limit(100)
    .fetch_all()
)
```

### Why this is worse than what we have

**Abstraction**

```python
# Builder: what API call is this making? What Front syntax does it produce?
convs = await ConversationQuery(client).status("open").tag("urgent").fetch_all()

# Helper: clear shape, Front syntax visible
convs = await client.conversations.list(q="status:open tag:urgent", limit=100)
```

**Type safety**

```python
# Builder: dynamic chaining means the type checker has to model every
# state transition. Autocomplete works in the best case, not always.
query.status("open").??? # what methods remain?

# Helper: IDE shows every kwarg at the call site
await client.conversations.list(
    q=,              # str | None
    limit=,          # int | None
    page_token=,     # str | None
    sort_by=,        # str | None
    sort_order=,     # str | None
)
```

**Debuggability**

```python
# Builder: step-through multiple methods before the API call
query = ConversationQuery(client).status("open")  # step 1
query = query.tag("urgent")                        # step 2
result = await query.fetch_all()                   # step 3 — API call somewhere in here

# Helper: single call, single breakpoint
convs = await client.conversations.list(q="status:open tag:urgent")
```

**Two ways to do everything**

```python
# If builders existed
convs = await ConversationQuery(client).status("open").fetch_all()

# And the helper still exists
convs = await client.conversations.list(q="status:open")

# Which should users pick? Which does the team prefer? What do we
# document as "the right way"?
```

## Alternatives considered

### Full builder pattern

Implement builders for every list endpoint.

**Rejected**: too much code (~30 builder classes), breaks transparency, hurts type
safety, and duplicates Front's `q=` syntax.

### Hybrid (builders for complex queries only)

Builders just for list endpoints with many parameters.

**Rejected**: creates two ways to do things, inconsistent API, still forces builder
maintenance.

### Partial application / bound client

```python
convs = client.conversations
result = await convs.list(q="status:open")
```

**Adopted** — this is exactly what the `client.conversations` helper is. Bound clients
give us the builder-like ergonomics of "set context once, call many times" without the
method-chaining surface. See
[`helpers/conversations.py`](../../helpers/conversations.py).

## What we do instead

### Domain helpers (from [ADR-0011](0011-pydantic-domain-models.md))

Ergonomic facades that wrap the generated API:

```python
# Helper gives us ergonomics without hiding anything
convs = await client.conversations.list(
    q="status:open tag:urgent",
    limit=100,
)
for c in convs:
    print(f"{c.id}: {c.subject} ({c.status})")

# The helper is a few lines over the generated API — easy to read
async def list(self, *, q=None, limit=None, page_token=None, ...):
    response = await list_conversations.asyncio_detailed(
        client=self._client, q=q, limit=limit, page_token=page_token,
    )
    parsed = unwrap(response)
    results = getattr(parsed, "field_results", None) or []
    return [Conversation.model_validate(c.to_dict()) for c in results]
```

### Front's search syntax

Front already provides an expressive query DSL via `q=`:

```python
convs = await client.conversations.list(
    q="status:open AND tag:urgent AND assignee:me AND after:2024-01-01",
)
```

This is the composition layer Front designed for this purpose — duplicating it in Python
would add surface area without benefit.

### Cookbook examples

Cookbook recipes demonstrate complex scenarios without needing new abstractions. See
[`frontapp_public_api_client/docs/cookbook.md`](../cookbook.md).

## When users ask for builders

If users request builders, explain the tradeoffs (this ADR), show the helper layer as
the alternative, and point to cookbook recipes. If the request persists with concrete
evidence that helpers + `q=` syntax are insufficient, revisit this decision — but carry
the bar for reintroducing a second API layer.

## References

- [ADR-0011: Pydantic Domain Models](0011-pydantic-domain-models.md) — the helper layer
- [ADR-002: OpenAPI Code Generation](0002-openapi-code-generation.md) — the generated
  layer
- [Front search syntax](https://dev.frontapp.com/docs/search-syntax) — Front's built-in
  DSL
- [`helpers/conversations.py`](../../helpers/conversations.py) — example of the pattern
- [`cookbook.md`](../cookbook.md)
