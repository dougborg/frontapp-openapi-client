---
name: new-vertical
description: >-
  Scaffold a new resource vertical end-to-end (helper + Pydantic domain + MCP
  tools + tests + docs). Use when starting a new "client.<resource>" surface
  such as drafts (#14), contacts (#2), messages (#4), tags/inboxes (#5).
  Requires the `vertical-planner` agent to produce a plan first.
argument-hint: "<issue-number-or-resource-name>"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit
  - Write
  - Bash(uv run poe quick-check)
  - Bash(uv run poe agent-check)
  - Bash(uv run poe check)
  - Bash(uv run poe fix)
  - Bash(uv run poe test *)
  - Bash(uv run pytest *)
  - Bash(ls *)
  - Bash(grep *)
  - Bash(gh issue view *)
  - Bash(git status)
  - Bash(git diff *)
  - Bash(git log *)
---

# New Vertical Scaffolding

Take a resource (issue # or name) from "not implemented" to "shipped behind a
green agent-check," following the canonical conversations vertical as the
template.

## PURPOSE

Encode the stereotyped vertical-shipping motion as a single repeatable workflow
so the resource-specific bits are the only thing the human (or coding agent)
has to think about. This is the harness for issues #2, #4, #5, #14, and any
future `client.<resource>` surface.

## CRITICAL

- **Plan first.** Invoke the `vertical-planner` agent before writing a single
  line of code. The plan must confirm generated module names and list-response
  shape (`field_results` vs raw array). Mid-implementation surprises waste a
  full debug cycle.
- **Mirror conversations/.** When in doubt, copy file structure, method names,
  and projection patterns from `helpers/conversations.py`,
  `domain/conversation.py`, and `tools/conversations.py`. Do not invent a new
  shape unless the resource genuinely differs.
- **Two-step confirm on mutations.** Every mutation tool takes
  `confirm: bool = False` and returns `ConfirmationResult`. **Exception:**
  drafts (#14) invert this — the draft IS the review step, so `create_draft`
  has no `confirm` param. Confirm against the issue before deviating.
- **Never edit files under `frontapp_public_api_client/api/`,
  `frontapp_public_api_client/models/`, or `client.py`** — those are generated.
  The `block-generated-edits.sh` PreToolUse hook will reject the attempt.

## ASSUMES

- The conversations vertical still works as the canonical template (run
  `uv run poe quick-check` to confirm before starting).
- The vendored spec is current. If you suspect upstream drift, run
  `/vendor-and-regen` first.
- A clean working tree on a feature branch, not `main`.

## STANDARD PATH

1. **Plan.** Invoke the `vertical-planner` agent with the issue # or resource
   name. Read its output. Do not proceed without a plan that names every
   generated module to wrap and flags any quirks.
2. **Domain projection.** Create
   `frontapp_public_api_client/domain/<resource>.py` — a Pydantic class extending
   `FrontappPydanticBase` that projects the response model. Convert epoch-second
   timestamps via the existing converters in `domain/converters.py`. Export
   from `domain/__init__.py`.
3. **Helper class.** Create `frontapp_public_api_client/helpers/<resource>.py`
   — a class extending `Base` with one async method per generated endpoint.
   Inside each method:
   - Lazy-import the generated `api/<tag>/<module>.py` and the domain class.
   - Build kwargs dict (only set keys for non-None args, to keep `UNSET`
     defaults from the generated signature).
   - Call `<module>.asyncio_detailed(**kwargs)`.
   - Unwrap with `unwrap_as(...)` for single objects, or
     `getattr(parsed, "field_results", None) or []` for lists. Use
     `is_success(...)` for 202/204.
   - Return Pydantic domain models, not generated attrs.
   Export from `helpers/__init__.py`.
4. **Wire into FrontappClient.** In `frontapp_client.py`:
   - Add `self._<resource>: <Class> | None = None` in `__init__`.
   - Add a lazy `@property` named `<resource>` returning the helper, mirroring
     the existing `conversations` property at line ~1098.
   - Add the `TYPE_CHECKING` import at the top.
5. **MCP tools.** Create
   `frontapp_mcp_server/src/frontapp_mcp/tools/<resource>.py` mirroring
   `tools/conversations.py`:
   - One `<Resource>Summary` Pydantic projection for compact LLM responses.
   - `def register_tools(mcp: FastMCP) -> None:` with one nested function per
     tool, decorated with `@mcp.tool(name=..., description=...)`.
   - Reads return list of summaries; mutations take `confirm: bool` and return
     `ConfirmationResult` (with the drafts-inverted exception).
   - Tools call `get_services(context).client.<resource>.<method>(...)`. Never
     reach into the generated `api/` modules from a tool.
6. **Register tools.** In
   `frontapp_mcp_server/src/frontapp_mcp/tools/__init__.py:register_all_tools`,
   add `from .<resource> import register_tools as register_<resource>_tools`
   then `register_<resource>_tools(mcp)`.
7. **Cache + instructions.** In
   `frontapp_mcp_server/src/frontapp_mcp/server.py`:
   - Append the new read-tool names to `_READ_ONLY_TOOLS`.
   - Extend the `instructions=` block with a section for the new resource —
     domain model description + tool selection guide + any search-syntax
     differences.
8. **Help resource.** Update
   `frontapp_mcp_server/src/frontapp_mcp/resources/help.py` Markdown to cover
   the new tools and parameters. **This is hand-maintained — do not assume the
   tool docstrings are enough.**
9. **Tests.** Add helper tests at `tests/test_<resource>.py` (mock httpx
   transport, exercise `unwrap_as` end-to-end) and MCP tool tests at
   `frontapp_mcp_server/tests/test_<resource>_tools.py`. Use
   `helpers/conversations.py` and existing `tests/test_conversations.py` as
   templates.
10. **README.** Flip the API Coverage row from ⏳ to ✅.
11. **Validate.** `uv run poe full-check`. Fix all errors at the source — no
    `noqa`, no `type: ignore`, no skips.

## EDGE CASES

- **Reference-resource only (issue #3 surfaces).** If the resource is meant to
  expose data as MCP **resources** (not tools) — e.g. `frontapp://teammates`
  or `frontapp://inboxes` — skip steps 5–7 and add a resource definition under
  `frontapp_mcp_server/src/frontapp_mcp/resources/` instead. Help text still
  needs updating.
- **Research vertical (issue #15 webhook receiver).** If the issue describes
  a new track (server-side webhooks, event streams) that doesn't fit the
  helper-+-domain-+-tools shape, escalate to the human before scaffolding —
  this skill assumes a CRUD-shaped resource.
- **Drafts invert confirm (issue #14).** `create_draft` does not take a
  `confirm` param; the draft itself is the review step. `update_draft` and
  `delete_draft` still use two-step confirm normally.
- **Generator quirks (`_a_` infix, `removes_` prefix).** Spec summaries that
  begin with "Update a …" / "Removes …" produce module names like
  `update_a_contact`, `removes_inbox_access`. Always `ls api/<tag>/` before
  writing the import — do not infer the name from the resource.
- **Raw-array list endpoints.** `/statuses` and `/teammates` return arrays
  directly, not wrapped in `field_results`. Unwrap as `unwrap(response)` and
  iterate the result directly.

## After

- Open a PR with `/open-pr` (the existing skill).
- Resolve the related issue (or note follow-up gaps in a comment).
- If new spec quirks were patched in `scripts/vendor_spec.py`, mention it in
  the PR description so reviewers know.
