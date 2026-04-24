# ADR-0011: Pydantic Domain Models for Business Entities

## Status

Accepted

Date: 2026-04-24

## Context

The generated attrs models from openapi-python-client represent API request/response
structures faithfully — they use `UNSET` sentinel values, carry everything the spec
declared, and are tightly coupled to the HTTP transport layer. That's the right shape
for transport but is suboptimal for:

1. **Business logic**: the `UNSET` sentinel requires constant `isinstance` checks and
   defensive unwrapping.
2. **LLM contexts**: passing the full `ConversationResponse` (including `_links`,
   `scheduled_reminders`, `metadata`, `custom_fields`, `ticket_ids`) into a model's
   context is wasteful — the useful subset is smaller.
3. **ETL / data processing**: `UNSET` complicates JSON export and database mapping.
4. **Immutability**: attrs models are mutable by default; domain code benefits from
   frozen objects.
5. **Timestamp ergonomics**: Front transmits `created_at` / `updated_at` as unix-seconds
   floats; callers want `datetime`.

## Decision

Provide **hand-written Pydantic v2 domain models** in
`frontapp_public_api_client.domain` as a parallel layer on top of the generated attrs
models. Hand-written, not auto-generated — the set of business-relevant entities is
small, and designing ergonomic projections is a judgment-call problem that benefits from
human authorship.

### Layered model architecture

```
frontapp_public_api_client/
├── models/            # attrs models — API transport layer (generated)
│                      # e.g. ConversationResponse, TagResponse,
│                      # TeammateResponse, RecipientResponse (complete)
└── domain/            # Pydantic models — business layer (hand-written)
    ├── base.py          # FrontappBaseModel (frozen, ignores extras)
    ├── converters.py    # to_unset / unwrap_unset helpers
    ├── conversation.py  # Conversation + TeammateSummary + TagSummary
    │                    #              + RecipientSummary
    └── (future)         # contact.py, message.py, etc.
```

### Design principles for domain models

1. **Frozen by default** — domain models are immutable; any mutation should go through
   the API, not in-memory field assignment.
2. **`extra="ignore"`** — domain models project a subset of the API response; ignoring
   unknown fields lets the upstream schema grow without breaking us.
3. **Unix timestamps → `AwareDatetime`** — every timestamp field uses a
   `@field_validator(mode="before")` that converts `int | float` to a UTC-aware
   `datetime`. Callers never deal with raw epoch seconds.
4. **Projection over copy** — domain models carry only the fields humans/agents actually
   reference. The full API object is always available one layer down if needed.
5. **Summary types for LLM responses** — MCP tool response types (e.g.
   `ConversationSummary` in `tools/conversations.py`) are even more compact projections,
   built specifically for LLM context economy.

### Convention for naming

- **`{Entity}`** — rich domain model mirroring the primary API response (e.g.
  `Conversation`, future `Contact`, `Message`).
- **`{Entity}Summary`** — compact nested projection used inside larger domain models
  (e.g. `TeammateSummary` inside `Conversation.assignee`, `TagSummary` inside
  `Conversation.tags`).
- **`{Entity}PageCursor`** — pagination cursors (e.g. `ConversationPageCursor`).

### Builder helpers for requests

Request-building helpers in `domain/converters.py`:

```python
from frontapp_public_api_client.domain.converters import to_unset, unwrap_unset

# Building an attrs request model from optional Pydantic fields
request = UpdateConversation(
    status=to_unset(status_input),      # None → UNSET; value → value
    assignee_id=to_unset(assignee_input),
)

# Reading an optional attrs field in business code
tags = unwrap_unset(conv.tags, default=[])
```

## Consequences

### Positive

- **Clean business API**: `Conversation.assignee.username` vs.
  `conv.assignee.username if not isinstance(conv.assignee, Unset) else None`
- **Immutability**: domain objects can be freely passed around without fear of mutation
- **Type safety**: Pydantic runtime validation catches shape mismatches at the boundary
  instead of deep in business logic
- **JSON schema**: domain models self-describe via `.model_json_schema()` — useful for
  MCP tool response schemas
- **LLM context economy**: projections keep tool responses small
- **Timestamp ergonomics**: callers work with `datetime`, not unix seconds

### Negative

- **Two model layers**: contributors must know when to use attrs (API transport) vs.
  Pydantic (business logic)
- **Hand-written maintenance**: unlike auto-generated models, domain types drift from
  the spec unless kept current. Mitigated by keeping domain models thin and
  reference-heavy (field names match API exactly, so drift is visible).
- **Conversion overhead**: small per-object cost to
  `Entity.model_validate(attrs_obj.to_dict())`. Negligible for typical workloads;
  significant at 100k+ objects/sec (which isn't our use case).

### Neutral

- **Generated attrs models remain unchanged**: no edits to `models/*.py`
- **Incremental adoption**: add domain models for resources as verticals ship
  (`Conversation` lives today; `Contact`, `Message`, etc. will arrive with their
  verticals)
- **No auto-generation pipeline required**: dropping auto-generation removes an entire
  script (`scripts/generate_pydantic_models.py`) and its datamodel-codegen dependency.
  The generated approach was appropriate for much larger domain surfaces (e.g. 150+
  entity types); at Front's scale, hand-written is the better trade.

## Example: the Conversation domain model

```python
# domain/conversation.py

class Conversation(BaseModel):
    id: str
    subject: str | None = None
    status: str | None = None
    status_category: str | None = None
    assignee: TeammateSummary | None = None
    recipient: RecipientSummary | None = None
    tags: list[TagSummary] = Field(default_factory=list)
    is_private: bool | None = None
    created_at: AwareDatetime | None = None
    updated_at: AwareDatetime | None = None
    waiting_since: AwareDatetime | None = None

    model_config = ConfigDict(
        frozen=True, str_strip_whitespace=True, extra="ignore",
    )

    @field_validator("created_at", "updated_at", "waiting_since", mode="before")
    @classmethod
    def _parse_timestamp(cls, value):
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=UTC)
        return value
```

Usage in a helper:

```python
# helpers/conversations.py

async def get(self, conversation_id: str) -> Conversation:
    response = await get_conversation_by_id.asyncio_detailed(
        conversation_id=conversation_id, client=self._client
    )
    parsed = unwrap(response)
    return Conversation.model_validate(parsed.to_dict())
```

The attrs → dict → Pydantic pattern is the standard boundary. Callers get a frozen
Pydantic `Conversation`; inside the helper, the generated attrs `ConversationResponse`
is still available for whoever wants it.

## Alternatives considered

### Auto-generate Pydantic models from the spec

Use `datamodel-code-generator` to emit a full parallel Pydantic model layer from
`docs/frontapp-openapi.yaml`.

**Pros**: complete coverage; generated in lockstep with the spec; bidirectional
`attrs ↔ pydantic` conversion.

**Cons**: full-model coverage is overkill when most API entities never surface in
business code; naming conflicts (`Status7`, `CustomField3`); auto-generation can't
produce the compact projections we actually want (`TeammateSummary` is not
`TeammateResponse`); adds `datamodel-code-generator` + a custom AST-fixup script as
dependencies.

**Rejected**: this was the prior project's approach. At Front's scale (~20 entities we'd
actually project), hand-written is cleaner and gives us better control over projection
shape.

### Skip the domain layer entirely

Have consumers call the generated attrs API directly, unwrap as needed.

**Pros**: no second model layer to maintain; one type system.

**Cons**: every caller reimplements `UNSET` handling, timestamp conversion, and
projection; MCP tools have no clean response shape to project into; LLM context balloons
on every tool call.

**Rejected**: the MCP layer is the strongest argument — LLM responses need to be small,
structured, and typed, which requires a projection layer somewhere.

### Use attrs throughout with wrapper methods

Keep attrs everywhere, add helper methods for convenience.

**Pros**: single model hierarchy.

**Cons**: attrs `@define` doesn't support validators cleanly; timestamp conversion
belongs in the type, not in helpers; `frozen=True` in attrs requires `@frozen` which
conflicts with our `@define` patterns.

**Rejected**: Pydantic v2 is the idiomatic choice for frozen, validated, typed domain
objects.

## References

- [ADR-002: Generate Client from OpenAPI Specification](0002-openapi-code-generation.md)
- [ADR-006: Response Unwrapping Utilities](0006-response-unwrapping-utilities.md)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [`domain/conversation.py`](../../domain/conversation.py) — current implementation
