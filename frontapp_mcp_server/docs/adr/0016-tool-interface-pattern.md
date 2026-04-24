# ADR-0016: Tool Interface Pattern

## Status

Accepted

Date: 2026-04-24

## Context

MCP tools need consistent, type-safe interfaces for requests and responses. We needed to
decide:

- How to structure tool parameters (flat vs. nested)
- How to handle validation
- How to represent responses (structured vs. string)
- How to integrate with FastMCP
- How to handle user confirmation for destructive operations

## Decision

Adopt the **Pydantic parameter annotations** pattern combined with **FastMCP
elicitation** for destructive operations. Frontapp tools use per-parameter
`Annotated[T, Field(description=...)]` directly rather than a nested request model +
`Unpack()` decorator — most tools have short argument lists and the per-parameter form
reads more naturally in the `@mcp.tool(...)` decorator shape.

The `Unpack()` decorator infrastructure (`frontapp_mcp/unpack.py`) is kept in-repo as an
option for future tools with wide or deeply-nested request bodies.

### Pattern components

#### 1. Per-parameter annotations (typical Frontapp tool)

```python
@mcp.tool(
    name="reply_to_conversation",
    description=(
        "Send an outbound reply on an existing conversation. Uses the "
        "channel the conversation was opened on. Two-step confirm."
    ),
)
async def reply_to_conversation(
    context: Context,
    conversation_id: str,
    body: Annotated[str, Field(description="Reply body (HTML or plain text)")],
    author_id: Annotated[
        str | None,
        Field(description="Teammate id to send as; defaults to token owner"),
    ] = None,
    subject: Annotated[str | None, Field(description="Override subject")] = None,
    to: Annotated[list[str] | None, Field(description="Override To recipients")] = None,
    cc: Annotated[list[str] | None, Field(description="CC recipients")] = None,
    bcc: Annotated[list[str] | None, Field(description="BCC recipients")] = None,
    confirm: Annotated[
        bool, Field(description="Must be true to send the reply")
    ] = False,
) -> dict[str, Any]:
    ...
```

#### 2. Request model + Unpack decorator (reserved for wide bodies)

When a future tool needs many fields or nested structure, wrap in a Pydantic model and
use `@unpack_pydantic_params`:

```python
class ImportMessageRequest(BaseModel):
    channel_id: str
    sender: SenderPayload
    body: str
    body_format: Literal["html", "markdown"] = "markdown"
    subject: str | None = None
    attachments: list[AttachmentPayload] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    confirm: bool = False


@unpack_pydantic_params
async def import_message(
    request: Annotated[ImportMessageRequest, Unpack()],
    context: Context,
) -> dict[str, Any]:
    ...
```

Use this form when a tool's argument list would exceed ~8 parameters or includes
deeply-nested structured data.

#### 3. Response shape

Read tools return typed Pydantic projections (`ConversationSummary`, future
`ContactSummary`, etc.) or raw attrs-to-dict lists. Mutation tools return a plain dict
with a consistent shape:

```python
# confirm=False (preview)
{
    "preview": {
        "action": "reply_to_conversation",
        "conversation_id": "cnv_abc",
        "body_preview": "Hi there…",
        ...
    },
    "confirmed": False,
}

# confirm=True, user cancelled elicitation
{
    "preview": {...},
    "confirmed": False,
    "result": "cancelled" | "declined",
}

# confirm=True, user approved, API succeeded
{
    "confirmed": True,
    "status_code": 202,  # HTTP status from Front
    "note": "Front returns 202 Accepted; the message is enqueued for delivery.",
}
```

Projection models (`ConversationSummary`) live in the same tool module that produces
them, not in the public domain package — they're LLM-context-optimized views of the
richer domain types.

#### 4. Two-step confirm pattern (safety-critical operations)

Every mutation tool takes `confirm: bool = False` and follows this shape:

```python
preview = {"action": "...", "conversation_id": conversation_id, ...}
if not confirm:
    return {"preview": preview, "confirmed": False}

result = await require_confirmation(
    context,
    f"Send reply to conversation {conversation_id}?",
)
if result is not ConfirmationResult.CONFIRMED:
    return {"preview": preview, "confirmed": False, "result": result.value}

# Proceed with the actual API call
response = await services.client.conversations.reply(...)
return {"confirmed": True, "status_code": response.status_code}
```

The pattern has two independent safety gates:

1. **Preview vs. execute**: `confirm=False` prevents accidental mutations from ambiguous
   LLM tool selection (the LLM has to explicitly re-call with `confirm=True`).
2. **Host elicitation**: `ctx.elicit` prompts the user even once the LLM has set
   `confirm=True`, so a misaligned LLM can't unilaterally apply changes.

#### 5. Shared schemas

Common schemas live in `frontapp_mcp/tools/schemas.py`:

```python
# frontapp_mcp/tools/schemas.py
class ConfirmationSchema(BaseModel):
    """Schema for user confirmation elicitation."""
    confirm: bool = Field(..., description="Confirm the action (true to proceed)")


class ConfirmationResult(StrEnum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    DECLINED = "declined"


async def require_confirmation(context: Context, message: str) -> ConfirmationResult:
    elicit_result = await context.elicit(message, ConfirmationSchema)
    if elicit_result.action != "accept":
        return ConfirmationResult.CANCELLED
    if not elicit_result.data.confirm:
        return ConfirmationResult.DECLINED
    return ConfirmationResult.CONFIRMED
```

Every mutation tool imports `ConfirmationResult` and `require_confirmation` so the
elicitation flow stays consistent.

### Benefits

- **Type safety**: Pydantic validates every input at runtime
- **Documentation**: Field descriptions surface in the MCP tool schema the LLM sees at
  registration
- **IDE support**: autocomplete and type checking work everywhere
- **Testability**: mutation tools in preview mode (`confirm=False`) can be tested
  without any API mocks
- **Consistency**: every mutation follows the same two-step confirm shape
- **Safety**: destructive operations require both an LLM affirm (`confirm=True`) and a
  user affirm (elicitation accept)

## Consequences

### Positive

- Type-safe tool interfaces prevent runtime errors
- Self-documenting parameters improve LLM tool selection and developer UX
- Validation errors are clear and actionable
- Elicitation prevents accidental destructive operations
- Shared helpers keep the confirm flow identical across tools

### Negative

- Per-parameter `Annotated[...]` annotations are verbose for wide signatures (resolved
  by dropping to Unpack for such tools)
- Two-step confirm means every mutation is at minimum a two-call flow, which is by
  design but trades latency for safety
- Elicitation round-trips add a user interaction step

### Neutral

- Currently 3 of 8 tools use elicitation (all three are mutations); future verticals are
  expected to follow the same ratio
- Preview dicts duplicate some argument structure, but the duplication is what lets
  users catch problems before they're applied

## Alternatives considered

### Flat untyped parameters

```python
async def reply_to_conversation(
    conversation_id: str,
    body: str,
    author_id: str | None,    # ❌ no Field description
    ...
    context: Context,
) -> dict:
    ...
```

**Rejected**: no validation, tool schemas lose field descriptions the LLM sees, harder
to keep tools consistent.

### Dictionary-based

```python
async def reply_to_conversation(
    params: dict,    # ❌ no type safety
    context: Context,
) -> dict:
    ...
```

**Rejected**: no IDE support, no validation, no documentation.

### Response-field confirmation (no elicitation)

```python
async def reply_to_conversation(...) -> dict:
    if not confirmed:
        return {"status": "pending", "confirmation_required": True}
    # else apply
```

**Rejected**: requires two full LLM round trips instead of one round trip plus host
elicitation, and bypasses the MCP host's UI for preview/confirm. The current pattern
lets Claude Desktop (and similar) show a proper dialog rather than surface a JSON field
the LLM has to interpret.

### Single confirm gate (no preview step)

Have `confirm=False` raise an error immediately instead of returning a preview.
**Rejected**: the preview is the LLM's sanity check — it lets the LLM (or user) verify
the intended action before committing, without requiring a speculative API call.

## Implementation examples

Live today in the conversations vertical (`tools/conversations.py`):

**Mutations** (two-step confirm + elicitation):

- `reply_to_conversation` — customer-facing outbound message
- `update_conversation` — archive/reopen, reassign, retag, move inbox
- `add_conversation_comment` — internal teammate note

**Reads** (no elicitation, cached 30s via `ResponseCachingMiddleware`):

- `list_conversations`, `get_conversation`, `search_conversations`,
  `list_conversation_messages`, `list_conversation_comments`

Future verticals (contacts, messages, tags, inboxes — see the repo's issue tracker) will
follow the same pattern.

## References

- [ADR-0017: Automated Tool Documentation](0017-automated-tool-documentation.md)
- [ADR-0011: Pydantic Domain Models](../../../frontapp_public_api_client/docs/adr/0011-pydantic-domain-models.md)
- [FastMCP](https://github.com/jlowin/fastmcp) — elicitation API
