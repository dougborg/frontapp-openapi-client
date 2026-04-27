# ADR-0010: Frontapp MCP Server Architecture

## Status

Accepted

Date: 2026-04-26

## Context

The `frontapp-mcp-server` package exposes Front's Core API as Model Context Protocol
tools so an AI assistant can list conversations, draft replies, manage tags, look up
contacts, and so on. Several questions had to be settled up front:

1. **Server framework** — implement MCP from scratch or adopt a library?
2. **Tool organization** — one giant `tools.py` or per-resource modules?
3. **Client lifecycle** — how does each tool get a `FrontappClient` without re-
   authenticating per call?
4. **Mutation safety** — how do we keep an autonomous agent from sending an email or
   deleting a contact without explicit human consent?
5. **Read caching** — Front's rate limit is shared across the whole workspace; how do we
   keep "list tags" / "list inboxes" from burning every tool call?
6. **Outbound replies** — should the server expose a "send reply now" tool, or force
   human review?

These decisions interact: the answers shape every new tool module added per vertical.

## Decision

The Frontapp MCP server is built on **FastMCP** with a per-resource tool layout, a
lifespan-managed `FrontappClient`, and a two-step confirm pattern on every mutation.
Outbound replies always go through the drafts surface — there is no programmatic send.

### 1. FastMCP + lifespan-managed `FrontappClient`

The server is a single `FastMCP("frontapp", lifespan=lifespan)` instance. The lifespan
context manager loads `FRONTAPP_API_KEY`, opens a `FrontappClient`, and exposes it via a
`Services` dependency-injection object that tools resolve through
`get_services(context)`:

```python
@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[Services]:
    async with FrontappClient(api_key=..., max_retries=5, max_pages=100) as client:
        yield Services(client=client)
```

```python
@mcp.tool(name="get_conversation", description="...")
async def get_conversation(context: Context, conversation_id: str) -> ConversationSummary:
    services = get_services(context)
    conv = await services.client.conversations.get(conversation_id)
    return to_summary(conv)
```

Auth lives in the FastMCP layer (bearer token via `MCP_AUTH_TOKEN` or GitHub OAuth via
`MCP_GITHUB_*`); see `_build_auth()` in `server.py`.

### 2. One tool module per resource (`tools/<resource>.py`)

Each vertical exports a `register_tools(mcp)` function that registers every tool for
that resource. `tools/__init__.py` exposes a single `register_all_tools(mcp)` entry
point that the server calls at startup:

```
tools/
├── __init__.py        # register_all_tools fan-out
├── schemas.py         # ConfirmationResult, require_confirmation
├── conversations.py   # 7 tools (5 read, 2 mutate)
├── contacts.py        # 12 tools
├── drafts.py          # 5 tools (drafts-first outbound — see ADR-0016)
├── inboxes.py         # ...
├── messages.py        # ...
├── tags.py            # ...
└── teammates.py       # ...
```

The mirror to `helpers/<resource>.py` (ADR-0007) is intentional: each tool module
delegates to the corresponding client helper. Tool code is thin glue — argument shaping,
projection to summary types, and the confirm gate.

### 3. Two-step confirm on every mutation

Every mutating tool takes a `confirm: bool = False` parameter. The pattern:

```python
async def update_conversation(
    context: Context,
    conversation_id: str,
    status: str | None = None,
    confirm: Annotated[bool, Field(description="Must be true to apply")] = False,
) -> dict[str, Any]:
    if not confirm:
        # Preview: return what would change without executing
        return {"action": "update_conversation", "preview": ..., "confirm_required": True}

    # Confirm via FastMCP elicitation — the client surfaces a yes/no prompt to the user
    result = await require_confirmation(
        context, f"Update conversation {conversation_id}?"
    )
    if result is not ConfirmationResult.CONFIRMED:
        return {"status": "cancelled", ...}

    # Execute
    services = get_services(context)
    await services.client.conversations.update(conversation_id, status=status)
    return {"status": "updated", ...}
```

`require_confirmation` (in `tools/schemas.py`) wraps
`ctx.elicit(message, ConfirmationSchema)` and returns one of `CONFIRMED` / `CANCELLED` /
`DECLINED`. The `confirm=False` preview path is the agent's contract: it sees what would
happen, can narrate it to the user, then re-invokes with `confirm=True` to actually
apply. The elicitation step is a second backstop — if the user is sitting at the client,
they explicitly approve before the call lands on Front.

The confirm gate is **per-tool**, not transport-level. Every mutating tool wires it in
the same shape; the helpers (ADR-0007) themselves don't gate.

### 4. Read tools are cached via `ResponseCachingMiddleware`

Read-only tools (every name in the `_READ_ONLY_TOOLS` set in `server.py`) go through
FastMCP's `ResponseCachingMiddleware` with a single shared TTL —
`CallToolSettings(ttl=30, included_tools=_READ_ONLY_TOOLS)` — plus
`ReadResourceSettings(ttl=60)` for reference resources (`frontapp://tags`,
`frontapp://inboxes`, `frontapp://teammates`). The cache lives in an in-memory
`MemoryStore`; it does not persist across restarts.

Caching is applied via the `_READ_ONLY_TOOLS` set so a new vertical only needs to extend
that set when adding read tools — no per-tool middleware wiring. If a future tool needs
a different TTL than 30s, a per-tool override can be added; today every cached tool
shares the 30s value.

### 5. Drafts-first outbound (no programmatic send)

There is **no `send_message` or `reply_to_conversation` tool** that bypasses human
review. Outbound replies are exclusively created as drafts via the `drafts` vertical
(`create_draft_reply`, `create_draft_on_channel`, `edit_draft`, `delete_draft`). The
draft lands in Front's UI; a human reviews and clicks send.

Draft mutations still use the §3 two-step confirm pattern (`confirm=False` returns a
preview; `confirm=True` plus `require_confirmation` executes), so the agent sees a
preview before the draft is even created. The drafts-first guarantee is at a higher
level: even after the draft lands, sending requires a human in Front's UI — there is no
programmatic send. See ADR-0016 → "Drafts-first outbound" for the full reasoning.

The `instructions=` block on the `FastMCP(...)` call documents this contract for the
agent at session start, including the rule "There is no programmatic 'send a reply now'
tool. By design — agents draft; humans send."

### 6. Domain-summary projections for tool responses

Tool responses use the `ConversationSummary` / `ContactSummary` / etc. projections from
`frontapp_mcp/projections.py`, not the full Pydantic domain models. Summaries strip the
fields LLMs don't need (`_links`, `metadata`, `custom_fields`, `ticket_ids`) to keep
tool-response token counts low. Full detail is one method call away if the agent needs
it.

## Consequences

### Positive

1. **Stereotyped vertical layout** — adding a new vertical is a copy-modify exercise.
   The mirror between `helpers/<resource>.py` (ADR-0007) and `tools/<resource>.py` keeps
   the surface predictable.
2. **Mutations are safe by default** — every destructive call surfaces a preview and a
   confirmation prompt before it lands. An agent that hasn't internalized "confirm:
   true" can't accidentally delete a contact.
3. **No surprise sends** — drafts-first outbound means the only way to reach a customer
   is through Front's UI, with a human in the loop. The MCP server cannot be tricked
   into dispatching a real reply.
4. **Read calls are cheap** — reference data (tags, inboxes, teammates) caches across
   tool invocations within a session. A long-running agent doesn't burn rate limit
   re-listing the workspace catalog every turn.
5. **One auth boundary** — `lifespan` initializes the client once. Tools never see the
   API key directly; they get a configured client through `Services`.
6. **Token economy** — summary projections keep tool responses small. The agent gets
   what it needs; the verbose API shape stays one layer down.

### Negative

1. **Tool-author discipline** — every new mutating tool has to wire the confirm gate by
   hand. Easy to forget. Mitigated by the canonical template (`tools/conversations.py`),
   the `vertical-planner` agent, and CI tests
   (`test_<resource>_tools_two_step_confirm`).
2. **No batch mutations** — each mutation requires its own confirm. An agent that wants
   to retag 50 conversations does 50 confirms. Acceptable: this is the safety floor.
3. **Cache invalidation is loose** — read caching is TTL-based with no per-mutation
   invalidation. After `update_tag(name=...)`, a `list_tags` call may briefly serve the
   stale name until the TTL expires. Acceptable for reference data; tools that need
   fresh state can call `get_*` directly.
4. **Two ways to read** — `client.conversations.get(...)` from Python code vs
   `get_conversation` from MCP. Both exist by design (the helper is the Pythonic entry
   point; the MCP tool is the agent-facing entry point) but the maintenance weight is
   real.

### Neutral

1. **`help.py` resource is hand-maintained** — the
   [Help resource drift](../../../CLAUDE.md#known-pitfalls) pitfall is that
   `resources/help.py` contains tool-doc Markdown that has to stay in sync with each
   tool module. ADR-0017 (Automated Tool Documentation) tracks moving this to generated
   content.
2. **`instructions=` is the runtime cheat-sheet** — the FastMCP `instructions` block in
   `server.py` is loaded into every agent session and is the canonical place to document
   tool-selection rules and safety patterns. New verticals add a section.
3. **Auth is optional** — bearer token / GitHub OAuth are env-configured and the server
   runs unauthenticated by default. Suitable for local dev; production deployments must
   set `MCP_AUTH_TOKEN` or `MCP_GITHUB_*`.

## Alternatives considered

### One giant `tools.py`

All tools registered in a single module.

**Rejected**: with ~50 tools across 7 verticals, the file would be unreadable. Per-
resource modules co-locate related tools and make it obvious where to add a new one.

### Confirm at the helper layer instead of per-tool

Move the two-step confirm into `client.conversations.update(..., confirm=True)`.

**Rejected**: the confirm gate is an MCP-runtime safety feature; the Python helper
shouldn't gate. Library callers (scripts, tests, application code) need to be able to
call mutations directly without a confirm dance — they're not in the agent threat model.

### Single `confirm=True` flag set at session start

Have the user enable an "agent autonomy" mode once, and skip per-call confirms
afterward.

**Rejected**: defeats the point. The two-step confirm exists to make every individual
mutation visible, not to gate the agent's general access. Per-call confirm is the safety
floor.

### Direct `send_reply` tool with a confirm gate

Provide `reply_to_conversation` with the standard two-step confirm.

**Rejected**: drafts-first is a stronger guarantee. Even with a confirm prompt, an agent
can hold context that misleads the user (wrong tone, wrong recipient, leaked secret) and
the user might confirm without catching it. Forcing the draft to land in Front's UI puts
the message in front of a human in its final form, in their actual inbox UI, before it
ships.

### Re-authenticate per tool call

Open a `FrontappClient` inside each tool function.

**Rejected**: kills connection reuse, multiplies env-var loads, and obscures the client
config. Lifespan management is the FastMCP-idiomatic pattern.

### Generate tool modules from helpers automatically

Auto-derive tool definitions from helper signatures.

**Rejected — for now**: the per-tool description, parameter docstrings, summary
projection shape, and confirm-gate logic involve enough judgment that codegen would be
more brittle than copy-modify. Revisit if the tool count grows past ~100 and the
hand-maintenance cost dominates.

## Implementation notes

### Adding a vertical's MCP tools

Encoded in the `/new-vertical` skill. Mirror the canonical template
(`tools/conversations.py`):

1. Create `tools/<resource>.py` with a `register_tools(mcp)` function.
2. For each helper method, write a `@mcp.tool(name=..., description=...)` async function
   that calls the helper through `get_services(context)`.
3. Mutations get `confirm: bool = False` + a preview branch + `require_confirmation`.
4. Wire `register_<resource>_tools(mcp)` into `tools/__init__.py:register_all_tools`.
5. Add read-only tool names to `_READ_ONLY_TOOLS` in `server.py` for caching.
6. Extend the `instructions=` block in `server.py` with a section on the new vertical
   (domain model, tool-selection guide, safety pattern).
7. Update `resources/help.py` Markdown — the help drift pitfall.
8. Tests: `test_<resource>_tools.py` covers reads and the two-step confirm flow for
   every mutating tool — confirm/elicitation cases live alongside the happy-path tests
   in the same module (e.g. `test_conversations_tools.py`).

### Why FastMCP

The MCP protocol has multiple Python implementations; FastMCP was chosen because:

- Built-in lifespan management via `@asynccontextmanager`
- First-class `ctx.elicit()` for the two-step confirm pattern
- Pydantic-native parameter annotations (ADR-0016 → "Tool Interface Pattern")
- Response caching middleware ships with the framework
- Maintained, with an active community and faster cadence on protocol updates than
  hand-rolling

### `_fastmcp_patches.py`

A small monkey-patch keeps FastMCP working with Pydantic 2.12+. Applied once at import
time before any tool is registered. See module docstring for details. Will be removed
when FastMCP upstream merges the equivalent fix.

## References

- [`server.py`](https://github.com/dougborg/frontapp-openapi-client/blob/main/frontapp_mcp_server/src/frontapp_mcp/server.py)
  — server entry point with lifespan + auth + caching
- [`tools/conversations.py`](https://github.com/dougborg/frontapp-openapi-client/blob/main/frontapp_mcp_server/src/frontapp_mcp/tools/conversations.py)
  — canonical tool-module template
- [`tools/schemas.py`](https://github.com/dougborg/frontapp-openapi-client/blob/main/frontapp_mcp_server/src/frontapp_mcp/tools/schemas.py)
  — `require_confirmation` and `ConfirmationResult`
- [`projections.py`](https://github.com/dougborg/frontapp-openapi-client/blob/main/frontapp_mcp_server/src/frontapp_mcp/projections.py)
  — summary projections for tool responses
- [ADR-0007: Domain Helper Classes](../../../frontapp_public_api_client/docs/adr/0007-domain-helper-classes.md)
  — the helper layer that every tool module delegates to
- [ADR-0016: Tool Interface Pattern](0016-tool-interface-pattern.md) — per-parameter
  Pydantic annotations and drafts-first outbound
- [ADR-0017: Automated Tool Documentation](0017-automated-tool-documentation.md) — the
  follow-up to remove `resources/help.py` drift
