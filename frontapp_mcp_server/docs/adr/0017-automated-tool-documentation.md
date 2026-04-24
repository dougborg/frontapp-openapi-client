# ADR-0017: Automated Tool Documentation

## Status

Accepted

Date: 2026-04-24

## Context

MCP tools need comprehensive documentation for both human developers and AI agents.
Documentation must be:

- **Accurate**: synchronized with implementation
- **Complete**: covers all tools and parameters
- **Discoverable**: easy to find and use
- **Multi-format**: serves different audiences (humans, LLMs, registry metadata)
- **Maintainable**: doesn't drift from the code

The challenge is balancing completeness with maintainability while serving multiple
audiences.

## Decision

Adopt a **multi-layered documentation approach** where code is the single source of
truth, with automated extraction for discovery and reference documentation.

### Documentation Layers

#### Layer 1: Python docstrings (primary source of truth)

Every tool carries a Google-style docstring:

```python
@mcp.tool(name="reply_to_conversation", description="...")
async def reply_to_conversation(
    context: Context,
    conversation_id: str,
    body: str,
    author_id: str | None = None,
    subject: str | None = None,
    to: list[str] | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    confirm: bool = False,
) -> dict[str, Any]:
    """Send an outbound reply on an existing Front conversation.

    🔴 HIGH-RISK OPERATION: customer-facing message. Requires two-step
    confirmation via ``ctx.elicit``.

    **Workflow**:
    1. Call with ``confirm=False`` — returns a preview of what would be
       sent (body, recipients, subject). No side effects.
    2. Call with ``confirm=True`` — elicits explicit user approval, then
       POSTs to ``/conversations/{id}/messages``. Front replies 202 Accepted;
       the message is enqueued for delivery on the conversation's channel.

    **Related tools**:
    - ``add_conversation_comment`` — internal teammate note (never reaches
      the customer)
    - ``update_conversation`` — archive/reassign without sending a reply

    **Related resources**:
    - ``frontapp://teammates`` — look up ``author_id`` values
    - ``frontapp://help`` — full tool reference

    Args:
        context: FastMCP context for services + elicitation
        conversation_id: Front conversation id, e.g. ``"cnv_abc123"``
        body: Reply body (HTML or plain text)
        author_id: Teammate id to send as; defaults to the token owner
        subject: Override subject (rarely needed)
        to / cc / bcc: Override recipients; defaults to the conversation's
            existing participants
        confirm: Must be True to actually send

    Returns:
        dict with ``confirmed``, ``status_code``, and a ``preview`` on the
        confirm=False branch

    Example:
        Preview:
            {"conversation_id": "cnv_abc", "body": "Thanks!", "confirm": false}
        Send:
            {"conversation_id": "cnv_abc", "body": "Thanks!", "confirm": true}
    """
```

**Required elements**:

- One-line summary
- Risk indicator for destructive operations (🔴 / 🟡 / 🟢)
- Workflow description
- Related tools / resources
- Full Args / Returns documentation
- At least one example

#### Layer 2: Pydantic field descriptions

Argument annotations use `Annotated[T, Field(description=...)]` so the descriptions
become part of the MCP tool schema and surface in MCP host UIs and LLM tool lists:

```python
async def list_conversations(
    context: Context,
    q: Annotated[
        str | None,
        Field(description=(
            "Front search syntax: status:open | tag:urgent | "
            "assignee:me | is:unassigned | inbox:support | "
            "after:2024-01-01 | before:2024-12-31 | AND/OR"
        )),
    ] = None,
    limit: Annotated[int | None, Field(description="Page size (max 100)")] = None,
    page_token: Annotated[str | None, Field(description="Cursor from pagination.next")] = None,
) -> list[ConversationSummary]:
    ...
```

**Requirements**:

- Every non-context argument gets a `Field(description=...)`
- Descriptions include expected format, examples, and constraints
- Request-body projection models (`ConversationSummary`, `ContactSummary`, etc.) carry
  field descriptions on output types too

#### Layer 3: Server-level instructions

`FastMCP(instructions=...)` in `server.py` carries the domain model, tool-selection
guide, Front search syntax reference, and safety patterns. Loaded into the MCP host's
context at session start so the LLM knows the overall shape of the tool surface before
picking a tool.

#### Layer 4: MCP resources for reference data

`frontapp://help` carries the full tool reference in Markdown. Additional
`frontapp://{tags,inboxes,teammates,conversations/recent}` resources (planned — see
issue tracker) expose workspace reference data so agents can orient themselves without
burning tool calls on lookups.

#### Layer 5: Tool metadata generator (optional)

`scripts/generate_tools_json.py` walks `frontapp_mcp/tools/` and emits a `tools.json`
for MCP registry submission:

```bash
uv run python scripts/generate_tools_json.py -o tools.json --pretty
```

It extracts tool names from `@mcp.tool(name=...)` decorators, descriptions from either
the decorator argument or the docstring's first line, and parameter schemas from the
function's `Annotated` types.

### Documentation standards

- **Docstring style**: Google (matches Python ecosystem conventions)
- **Field descriptions**: complete sentences with punctuation
- **Examples**: real-world request/response pairs inside docstrings
- **Cross-references**: link to related tools, resources, and ADRs

## Consequences

### Positive

- **Always accurate**: code is documentation — it can't get out of sync
- **Multi-audience**: same source serves IDE hovers, MCP schemas, registry metadata, and
  LLM context
- **Discoverable**: tools are self-documenting via metadata
- **IDE support**: docstrings + type hints give rich autocomplete and hover help
- **LLM-friendly**: Field descriptions become part of the tool schema the LLM sees at
  registration time

### Negative

- **Verbose docstrings**: the required detail makes tools longer
- **Upfront work**: each tool needs comprehensive documentation before shipping
- **Generator maintenance**: `generate_tools_json.py` must track decorator and typing
  changes

### Neutral

- **Convention over configuration**: strict standards reduce flexibility but increase
  consistency across tool modules
- **Documentation review**: PRs require doc review alongside code review

## Documentation workflow

### Adding a new tool

1. Write the docstring following Layer 1 standards
2. Annotate every argument with `Annotated[..., Field(description=...)]`
3. Update `server.py` `instructions` if the new tool introduces a new workflow or
   resource
4. Update `resources/help.py` to list the tool in the right section
5. Run `scripts/generate_tools_json.py` to regenerate registry metadata
6. Add tool tests under `frontapp_mcp_server/tests/tools/` exercising both preview and
   confirm paths on any mutation

### Maintaining documentation

- **Code changes**: update docstrings and field descriptions in lockstep
- **Examples**: keep example request/response pairs current with Front's API
- **Metadata**: regenerate `tools.json` before each release
- **help.py**: keep the Markdown help resource in sync when tool names or semantics
  change — this is surfaced to the LLM via MCP and drift hurts usability

## Alternatives considered

### External documentation only

Keep comprehensive docs in separate Markdown, with minimal docstrings in code.
**Rejected** because docs drift quickly, IDE support regresses, and LLMs reading the MCP
schema lose detail.

### Minimal docstrings + separate reference

Brief one-line docstrings, detailed docs maintained separately. **Rejected** for the
same drift/discoverability reasons. Brief docstrings also hurt context-switching.

### Auto-generate from OpenAPI

Generate all MCP documentation from Front's OpenAPI spec. **Rejected** because MCP tools
don't map 1:1 to API endpoints — they're higher-level workflows (two-step confirm,
projected summaries, search-syntax convenience) that the spec doesn't capture. Upstream
Front descriptions are also often terse one-liners not suited to LLM tool selection.

### Template-first responses

Require Markdown templates for every tool response. **Rejected** as overkill — Frontapp
tool responses are small JSON objects and a Pydantic projection model
(`ConversationSummary`) already provides the necessary structure.

## Implementation status

**Fully implemented**:

- Layer 1 (docstrings) — all tools in the conversations vertical ✅
- Layer 2 (Annotated field descriptions) — all tool arguments ✅
- Layer 3 (server.py instructions) — Front domain model, tool selection guide, search
  syntax reference ✅
- Layer 4 (`frontapp://help` resource) — kept in sync with the tool surface ✅

**Deferred**:

- Layer 5 (`generate_tools_json.py`) — the generator script is in-repo but regeneration
  isn't wired into CI yet
- Additional `frontapp://{tags,inboxes,teammates,conversations/recent}` resources
  (tracked as an issue)

**Documentation coverage** (as of this writing):

- 8 conversation tools (5 read-only, 3 mutations with two-step confirm)
- 1 resource (`frontapp://help`)
- Additional verticals (contacts, messages, tags, inboxes, analytics) tracked as issues

## Tool documentation examples

**Read-only tool** (`list_conversations`):

- 🟢 indicator (safe, no confirmation needed)
- Example query using Front search syntax
- Cursor pagination explained

**Destructive tool** (`reply_to_conversation`):

- 🔴 indicator (customer-facing mutation)
- Two-step confirm workflow documented
- Preview vs. confirm modes explained
- 202 Accepted / async-enqueue semantics noted

**Destructive internal tool** (`add_conversation_comment`):

- 🟡 indicator — mutation but not customer-visible
- Same two-step confirm pattern for consistency

## References

- [ADR-0016: Tool Interface Pattern](0016-tool-interface-pattern.md)
- [ADR-004: Defer Observability to httpx](../../../frontapp_public_api_client/docs/adr/0004-defer-observability-to-httpx.md)
- [`scripts/generate_tools_json.py`](../../../scripts/generate_tools_json.py) — metadata
  generator
- [`frontapp_mcp/resources/help.py`](../../src/frontapp_mcp/resources/help.py) — help
  Markdown
- [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
