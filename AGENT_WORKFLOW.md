# Agent Workflow Guide

Step-by-step guide for AI agents (Claude Code, Copilot, others) developing this repo.
Pairs with `CLAUDE.md` — that file is the cheat-sheet, this one is the walkthrough.

> **Quickest path:** read CLAUDE.md → check `docs/api-facts.yaml` for any
> resource-specific question → invoke `vertical-planner` before coding a new resource →
> use `/new-vertical` to scaffold → `/open-pr` when done.

---

## Knowledge sources, in priority order

When you have a question about the codebase, consult these in order. Stop at the first
one that answers your question:

1. **`docs/api-facts.yaml`** — generated, CI-validated index of every endpoint.
   Pre-computed reverse indexes in `summary.*` answer most factual questions in one
   grep. Cannot drift from the generated tree.
2. **`CLAUDE.md`** — architecture, validation tiers, anti-patterns, file rules. The
   cheat-sheet.
3. **The canonical templates** — `frontapp_public_api_client/helpers/conversations.py`,
   `frontapp_public_api_client/domain/conversation.py`,
   `frontapp_mcp_server/src/frontapp_mcp/tools/conversations.py`. These are the patterns
   every new vertical should mirror.
4. **`docs/adr/`** — architecture decision records, slow-changing prose. Read when the
   "why" of a pattern matters.
5. **The OpenAPI spec** (`docs/frontapp-openapi.yaml`) — request body shapes, field
   types, error responses. Read when the facts file doesn't have what you need.
6. **Direct grep / file inspection** — last resort. If you find yourself here often for
   the same question, the facts file or CLAUDE.md probably needs an update.

---

## Sub-agents and skills

The `.claude/` tree provides specialized agents and workflow skills.

### Sub-agents (`.claude/agents/`)

Spawn these for delegated work during complex tasks. They have their own knowledge
sources and tool restrictions baked in via frontmatter.

| Agent              | When to use                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| `vertical-planner` | Before writing a new `client.<resource>` surface — produces a structured plan.  |
| `domain-advisor`   | One-off factual questions ("does list_X use field_results?"). Read-only oracle. |
| `code-modernizer`  | Refactoring hand-written code to current patterns (UNSET helpers, unwrap, etc.) |
| `pr-preparer`      | Branch-readiness check before opening a PR                                      |
| `spec-auditor`     | Audit the vendored spec against upstream for drift                              |

### Skills (`.claude/skills/`)

Multi-step workflows. Invoked as `/skill-name`.

| Skill               | What it does                                                                                      |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| `/new-vertical`     | End-to-end vertical scaffolding (helper + domain + MCP tools + tests + docs).                     |
| `/vendor-and-regen` | Refresh the vendored OpenAPI spec from upstream and regenerate the client safely.                 |
| `/open-pr`          | Open a PR — self-review, push, create, wait for CI, address feedback.                             |
| `/review-pr`        | Address PR review comments — fetch, fix, validate, push, reply. Handles stacked PRs and Disagree. |
| `/review`           | Structured code review of the current branch.                                                     |
| `/techdebt`         | Scan for repo-specific anti-patterns.                                                             |
| `/write-tests`      | Generate tests for target code (mock httpx transport, exercise unwrap helpers).                   |
| `/generate-docs`    | Generate or update ADRs / cookbook entries.                                                       |
| `/verify`           | Skeptical validation pass before considering work complete.                                       |
| `/pre-commit`       | Quick pre-flight before committing.                                                               |

### Hooks (`.claude/hooks/`)

Automatic safety net wired in via `.claude/settings.json`.

| Hook                       | When it fires                             | What it does                                                                                                                                                                                                                        |
| -------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `block-generated-edits.sh` | PreToolUse on `Edit`/`Write`/`MultiEdit`  | Blocks edits to generated/vendored files under `frontapp_public_api_client/` (`api/**`, `models/**`, `client.py`, `client_types.py`, `errors.py`) and the two vendored YAMLs (`docs/frontapp-openapi.yaml`, `docs/api-facts.yaml`). |
| `format-on-edit.sh`        | PostToolUse on `Edit`/`Write`/`MultiEdit` | Silently runs `ruff format`+`check --fix` on `*.py` and `prettier --write` on `*.md`.                                                                                                                                               |

---

## The vertical-shipping workflow

"Ship a new resource vertical" (drafts, contacts, messages, tags/inboxes, etc.) is the
primary recurring unit of work. The harness encodes it as a five-step motion:

1. **Plan** — `vertical-planner` reads `docs/api-facts.yaml` for the resource and
   produces a structured plan (modules to wrap, response shapes, helper + domain wiring
   status, MCP tools to register, files to create vs edit, risks). Output is reviewed
   before any code is written.
2. **Scaffold** — `/new-vertical` walks the 12-step STANDARD PATH (domain projection →
   helper class → wire into `FrontappClient` → MCP tools → register → cache +
   instructions → help.py → tests → README → validate). Mirrors
   `frontapp_public_api_client/helpers/conversations.py` +
   `frontapp_mcp_server/src/frontapp_mcp/tools/conversations.py` as the canonical
   templates.
3. **Validate** — `uv run poe full-check` (Tier 4) before requesting review. See
   "Validation tiers" below.
4. **Open PR** — `/open-pr` self-reviews, pushes, opens the PR, waits for CI.
5. **Self-review with `/simplify`** — once CI is green, run `/simplify` to spawn three
   parallel review agents (reuse, quality, efficiency) on the diff. Catches real bugs
   (broken type annotations, DRY misses, unused imports) before an external reviewer
   flags them. Fold any findings into a `fixup!` commit.
6. **Address feedback** — `/review-pr` handles external review comments.

Steps 5 + 6 are routine for every vertical / feature PR — not optional polish. The
`/open-pr` skill encodes this as Phase 7 (`/simplify`) and Phase 8 (`/review-pr`).

If something doesn't fit the canonical template (drafts inverts the two-step-confirm,
reference-only resources go through `resources/` not `tools/`), the planner flags it
under "Risks" — those become explicit decisions, not mid-implementation surprises.

---

## Validation tiers

Run the appropriate tier for your stage. Each is a poe task; see CLAUDE.md "Essential
Commands" for timings.

| Tier | Task                     | When                                             |
| ---- | ------------------------ | ------------------------------------------------ |
| 1    | `uv run poe quick-check` | During development — fast format + lint feedback |
| 2    | `uv run poe agent-check` | Before committing — adds typecheck + facts-check |
| 3    | `uv run poe check`       | Before opening a PR — adds tests                 |
| 4    | `uv run poe full-check`  | Before requesting review — adds docs-build       |

`agent-check`, `check`, and `full-check` all include `facts-check`, so the generated
`docs/api-facts.yaml` cannot drift from the api/ tree.

If validation fails, fix at the source — never `noqa`, `type: ignore`, `--no-verify`, or
skip a test. See CLAUDE.md "Zero Tolerance for Ignoring Errors".

---

## Common pitfalls

CLAUDE.md "Known Pitfalls" is the canonical list. Highlights an agent reading this file
once should remember:

- **Generated files** —
  `frontapp_public_api_client/{api/**, models/**, client.py, client_types.py, errors.py}`
  plus the vendored YAMLs `docs/frontapp-openapi.yaml` and `docs/api-facts.yaml`. Never
  edit directly; the PreToolUse hook will reject. Regenerate via the appropriate
  pipeline command (`uv run poe regenerate-client`, `uv run poe facts`, or
  `uv run poe regenerate-all`).
- **`field_results` vs raw arrays** — most list endpoints wrap results in
  `field_results` (openapi-python-client renames Front's `_results`). A few return raw
  arrays. Consult `docs/api-facts.yaml` `summary.*`; do not guess by tag name.
- **`UNSET` sentinel** — attrs models use `UNSET` for unprovided fields, not `None`. Use
  `unwrap_unset(field, default)` from `frontapp_public_api_client/domain/converters.py`,
  not `isinstance` or `hasattr` checks. Use `to_unset(value)` when building request
  bodies.
- **MCP mutation pattern** — every mutating tool takes `confirm: bool = False`, builds a
  `preview` dict, then runs the gate via `confirm_or_preview` from
  `frontapp_mcp/tools/schemas.py`:

  ```python
  preview = {"action": "...", ...}
  gate = await confirm_or_preview(
      context, preview=preview, confirm=confirm,
      elicit_message=f"Concrete prompt the user sees?",
  )
  if gate is not None:
      return gate
  # ... proceed with mutation
  ```

  `confirm_or_preview` returns the response dict to bail with on the preview / declined
  paths, or `None` when the caller should proceed. Don't hand-roll the 6-line
  `if not confirm: ... require_confirmation ... ConfirmationResult.CONFIRMED` cascade.
  The underlying `ConfirmationResult` StrEnum is now an implementation detail; only
  import it directly if a tool needs to branch on `DECLINED` vs `CANCELLED` (rare).

- **`/review-pr` on stacked PRs** — when merging a parent with `--delete-branch`, flip
  every child's base to `main` first, otherwise GitHub auto-closes them (and they can't
  be reopened). The `/review-pr` skill has a full section on this.

---

## Working with the LSP tool

For type/call-graph questions inside hand-written code, **prefer LSP operations over
`Read`+`Grep`** — they're faster, more accurate, and cross-reference the real type
system (including third-party libraries in `.venv`). Both Python (pyright) and
TypeScript (typescript-language-server) LSPs are configured and active.

| When you need to…                                                 | Use                  |
| ----------------------------------------------------------------- | -------------------- |
| Understand a symbol's type/signature/docstring                    | `LSP hover`          |
| Jump to where a function/class is defined                         | `LSP goToDefinition` |
| **Find every caller of a function before changing its signature** | `LSP findReferences` |
| List all symbols in a file (skim without reading the whole thing) | `LSP documentSymbol` |
| Trace callers of a function (who calls X?)                        | `LSP incomingCalls`  |
| Trace callees of a function (what does X call?)                   | `LSP outgoingCalls`  |

**Concrete situations where reaching for LSP wins over `Read`/`Grep`:**

- **Before extracting a helper or renaming a symbol** — `LSP findReferences` on the
  symbol gives you the exact set of files that need updating. Saves a "missed one
  caller" bug.
- **Before changing a function signature** — `LSP findReferences` then `LSP hover` on
  each caller to see the call site shape. Avoids surprise type errors at validation
  time.
- **When designing a new helper class that mirrors an existing one** —
  `LSP documentSymbol` on the canonical (e.g. `helpers/contacts.py`) gives you the full
  method list in seconds, no `Read` needed.
- **When chasing why a test fails on an attribute access** — `LSP hover` on the
  attribute tells you whether the type is `Unset` / `None` / domain model, including
  fields from third-party libs.
- **When refactoring touches 30+ files** — never grep + edit blindly.
  `LSP findReferences` gives you the precise call graph, then a small Python script can
  rewrite the matches mechanically. (Lesson from the PR that introduced
  `confirm_or_preview` — grep-driven refactor missed several formatting variants the
  regex didn't catch.)

For project-wide symbol search, fall back to `Grep` — pyright only indexes _open_ files
in this configuration, so `LSP workspaceSymbol` returns nothing. Other known limitations
(`goToImplementation` not implemented, external-import `goToDefinition` returns nothing
— use `hover` instead) are listed in CLAUDE.md "LSP known limitations".

---

## Multi-agent / parallel work

If multiple agents are working on the project simultaneously:

1. Each takes their own branch (`feat/<resource>-vertical`, `chore/<area>-cleanup`).
2. The PreToolUse hook + `facts-check` CI gate prevent the most common collision modes
   (generated-file edits, stale fact index).
3. For overlapping changes, the second-to-merge rebases via `/review-pr`'s stacked-PR
   section.
4. `/babysit-prs` watches CI on every open PR in parallel, surfaces real (non-flaky)
   failures with their job-log tails, and chains into `/review-pr` when comments arrive
   — see `.claude/skills/babysit-prs/SKILL.md`.

---

## Detailed references

- `CLAUDE.md` — quick-reference cheat-sheet; **read this first**
- `docs/api-facts.yaml` — generated, machine-readable index of every endpoint
- `docs/adr/README.md` — architecture decision records
- `frontapp_public_api_client/docs/guide.md` — Python client guide
- `frontapp_mcp_server/docs/README.md` — MCP server docs
- `packages/frontapp-client/README.md` — TypeScript client

---

## Self-improvement

If you discover something that should be in this guide, CLAUDE.md, or one of the skill
prompts, update it as part of your current work. Stale agent guidance is more harmful
than no guidance — see CLAUDE.md "Continuous Improvement". The session that documented
an anti-pattern as the canonical example wasted three later sessions before it was
caught.
