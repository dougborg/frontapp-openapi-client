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

Adopt the **Pydantic parameter annotations** pattern combined with a **two-call
preview/execute gate** for destructive operations. Frontapp tools use per-parameter
`Annotated[T, Field(description=...)]` directly rather than a nested request model +
`Unpack()` decorator — most tools have short argument lists and the per-parameter form
reads more naturally in the `@mcp.tool(...)` decorator shape.

The original revision of this ADR also relied on `ctx.elicit` for a server-side
confirmation prompt. That layer was removed because elicitation is unreliable across MCP
clients, notably broken in Claude Desktop. Per the MCP Tools spec, clients SHOULD
prompt; servers SHOULD NOT.

The `Unpack()` decorator infrastructure (`frontapp_mcp/unpack.py`) is kept in-repo as an
option for future tools with wide or deeply-nested request bodies.

### Pattern components

#### 1. Per-parameter annotations (typical Frontapp tool)

```python
@mcp.tool(
    name="create_draft_reply",
    description=(
        "Create a draft reply on an existing conversation. The human reviews "
        "the draft in Front and clicks send. Two-step confirm."
    ),
)
async def create_draft_reply(
    context: Context,
    conversation_id: str,
    body: Annotated[str, Field(description="Reply body (HTML or plain text)")],
    channel_id: Annotated[
        str, Field(description="Channel to send through, e.g. 'cha_xyz'")
    ],
    author_id: Annotated[
        str | None,
        Field(description="Teammate id to author as; defaults to token owner"),
    ] = None,
    subject: Annotated[str | None, Field(description="Override subject")] = None,
    to: Annotated[list[str] | None, Field(description="Override To recipients")] = None,
    cc: Annotated[list[str] | None, Field(description="CC recipients")] = None,
    bcc: Annotated[list[str] | None, Field(description="BCC recipients")] = None,
    confirm: Annotated[
        bool, Field(description="Must be true to create the draft")
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
        "action": "create_draft_reply",
        "conversation_id": "cnv_abc",
        "body_preview": "Hi there…",
        ...
    },
    "confirmed": False,
}

# confirm=True, API succeeded
{
    "confirmed": True,
    "status_code": 202,  # HTTP status from Front
    "note": "Front returns 202 Accepted; the message is enqueued for delivery.",
}
```

Projection models (`ConversationSummary`) live in `frontapp_mcp.projections` — a shared
module imported by both the tool surface and any reference resource that returns the
same shape. They're LLM-context-optimized views of the richer domain types and are
deliberately separate from the public domain package.

#### 4. Two-step confirm pattern (safety-critical operations)

Every mutation tool takes `confirm: bool = False` and runs the gate via the
`confirm_or_preview` helper from `frontapp_mcp/tools/schemas.py`:

```python
preview = {"action": "...", "conversation_id": conversation_id, ...}

gate = confirm_or_preview(preview=preview, confirm=confirm)
if gate is not None:
    return gate

# Proceed with the actual API call
response = await services.client.conversations.reply(...)
return {"confirmed": True, "status_code": response.status_code}
```

`confirm_or_preview` returns the dict the tool should bail with on the preview path
(`confirm=False`), or `None` when the caller should proceed. The contract is
**two-call**: the LLM first invokes the tool with `confirm=False` to get the preview,
surfaces it to the user, and only re-invokes with `confirm=True` after the user has
agreed.

The single safety gate is in-band:

1. **Preview vs. execute**: `confirm=False` prevents accidental mutations from ambiguous
   LLM tool selection. The LLM must show the preview to the user and explicitly re-call
   with `confirm=True` once the user has agreed.

Earlier revisions of this ADR also relied on `ctx.elicit` for a server-side confirmation
prompt. That layer was removed because elicitation is unreliable across MCP clients
(notably broken in Claude Desktop and several others — the elicit call never resolves,
so the user never sees the prompt and the mutation never executes). Per the MCP Tools
spec, **clients SHOULD prompt users; servers SHOULD NOT**. Spec-compliant clients should
be configured to prompt for tools annotated with `destructiveHint=True`; that work is
tracked separately.

#### 5. Drafts-first outbound

For customer-facing replies there is a **second** gate beyond preview/execute: the agent
never sends, it only drafts. The Frontapp drafts vertical (`create_draft_reply`,
`create_draft_on_channel`, `edit_draft`, `delete_draft`) exposes the full reply surface,
but Front's API has no programmatic `send_draft` — the human reviews the draft in
Front's UI and clicks send themselves.

The earlier `reply_to_conversation` tool (which sent immediately on `confirm=True`) was
removed in the drafts vertical PR. Even a misaligned LLM that gets past the preview gate
cannot send to a customer; the strongest action it can take is creating a draft that a
human still has to approve and dispatch.

This also matches Front's product model — every outbound message in Front flows through
a draft state, even when teammates type-and-send by hand. The agent surface just keeps
that behavior explicit.

Mutation tools that don't reach the customer (`update_conversation`,
`add_conversation_comment`) keep the standard two-gate pattern only. The drafts-first
rule is specifically for outbound messaging.

#### 6. Shared schemas

The shared confirmation gate lives in `frontapp_mcp/tools/schemas.py`:

```python
# frontapp_mcp/tools/schemas.py
def confirm_or_preview(
    *,
    preview: dict[str, Any],
    confirm: bool,
) -> dict[str, Any] | None:
    """Two-call preview/execute gate. Returns the response dict the caller
    should return verbatim on the preview path (`confirm=False`), or None
    when the caller should proceed with the mutation.
    """
    if not confirm:
        return {"preview": preview, "confirmed": False}
    return None
```

Every mutation tool imports `confirm_or_preview` and calls it once instead of
hand-rolling the cascade.

### Benefits

- **Type safety**: Pydantic validates every input at runtime
- **Documentation**: Field descriptions surface in the MCP tool schema the LLM sees at
  registration
- **IDE support**: autocomplete and type checking work everywhere
- **Testability**: mutation tools in preview mode (`confirm=False`) can be tested
  without any API mocks
- **Consistency**: every mutation follows the same two-call preview/execute shape
- **Safety**: destructive operations require an explicit re-invocation with
  `confirm=True` after the user has agreed to the preview

## Consequences

### Positive

- Type-safe tool interfaces prevent runtime errors
- Self-documenting parameters improve LLM tool selection and developer UX
- Validation errors are clear and actionable
- Two-call preview/execute prevents accidental destructive operations
- Shared helpers keep the confirm flow identical across tools

### Negative

- Per-parameter `Annotated[...]` annotations are verbose for wide signatures (resolved
  by dropping to Unpack for such tools)
- Two-step confirm means every mutation is at minimum a two-call flow, which is by
  design but trades latency for safety

### Neutral

- Preview dicts duplicate some argument structure, but the duplication is what lets
  users catch problems before they're applied

## Alternatives considered

### Flat untyped parameters

```python
async def create_draft_reply(
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
async def create_draft_reply(
    params: dict,    # ❌ no type safety
    context: Context,
) -> dict:
    ...
```

**Rejected**: no IDE support, no validation, no documentation.

### Server-side elicitation (`ctx.elicit`)

Earlier revisions of this ADR specified `ctx.elicit` as a second backstop after the
preview step — the server would prompt the user for confirmation even after
`confirm=True`. **Reverted**: elicitation is unreliable across MCP clients and is broken
outright in Claude Desktop (the elicit call never resolves, so the user never sees the
prompt and the mutation never executes). Per the MCP Tools spec, clients SHOULD prompt;
servers SHOULD NOT. The recommended client-side cue is the `destructiveHint` annotation,
tracked separately.

### Single confirm gate (no preview step)

Have `confirm=False` raise an error immediately instead of returning a preview.
**Rejected**: the preview is the LLM's sanity check — it lets the LLM (or user) verify
the intended action before committing, without requiring a speculative API call.

## Implementation examples

Live today across the conversations and drafts verticals:

**Mutations** (two-call preview/execute):

- `create_draft_reply` / `create_draft_on_channel` / `edit_draft` / `delete_draft` — the
  drafts vertical (`tools/drafts.py`); customer-facing outbound always goes through
  drafts
- `update_conversation` — archive/reopen, reassign, retag, move inbox
- `add_conversation_comment` — internal teammate note

**Reads** (no confirm gate, cached 30s via `ResponseCachingMiddleware`):

- `list_conversations`, `get_conversation`, `search_conversations`,
  `list_conversation_messages`, `list_conversation_comments`

Future verticals (contacts, messages, tags, inboxes — see the repo's issue tracker) will
follow the same pattern.

## References

- [ADR-0017: Automated Tool Documentation](0017-automated-tool-documentation.md)
- [ADR-0011: Pydantic Domain Models](https://github.com/dougborg/frontapp-openapi-client/blob/main/frontapp_public_api_client/docs/adr/0011-pydantic-domain-models.md)
- [FastMCP](https://github.com/jlowin/fastmcp)
