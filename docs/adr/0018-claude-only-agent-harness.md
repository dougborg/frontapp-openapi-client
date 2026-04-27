# ADR-0018: Claude-only Agent Harness

## Status

Accepted

Date: 2026-04-26

Supersedes
[ADR-0014: GitHub Copilot Custom Agents](0014-github-copilot-custom-agents.md).

## Context

[ADR-0014](0014-github-copilot-custom-agents.md) established a parallel GitHub Copilot
harness — `.github/agents/`, `.github/instructions/`, `.github/prompts/`,
`.github/agents/guides/` — alongside the Claude harness in `.claude/`. The intent was to
support both runtimes equally.

In practice, every recent feature has been shipped through the Claude harness
(conversations, contacts, drafts, messages, tags, inboxes, teammates verticals;
auto-pagination iterators; transport-stack tests; the `vertical-planner` and
`domain-advisor` agents; `/new-vertical`, `/vendor-and-regen`, `/open-pr`, `/review-pr`,
`/babysit-prs` skills). The Copilot harness has not been used to drive any vertical and
has accumulated drift:

- The agent files (`*.agent.md`) referenced `@agent-dev` / `@agent-test` agents that
  don't exist (issue #32).
- `python-developer.agent.md` showed `if response.status_code == 200` as example code —
  the documented anti-pattern in CLAUDE.md (issue #17 Phase A).
- `.github/agents/guides/` — ~7,300 lines across 15 files — was inherited from a
  StatusPro template and contained inventory/manufacturing examples, `purchase_order`
  references, and `sku` fields that have nothing to do with Front (issue #39).
- `.github/instructions/python-mcp-server.instructions.md` referenced `check_inventory`;
  `python.instructions.md` referenced `product_id`; `pytest.instructions.md` validated
  `sku`.
- The shared/ guides duplicated content already in `CLAUDE.md` and `AGENT_WORKFLOW.md`
  with stale numbers ("100+ API endpoints" vs the actual 233).

Three options were on the table:

1. **Keep + rewrite** the Copilot harness to match Front's domain (~hours of pure
   docs-rewriting work, with no evidence the resulting files would get used).
2. **Keep as-is and tolerate drift** — every future cleanup PR rediscovers the same
   StatusPro examples and proposes the same fixes.
3. **Remove the Copilot harness** entirely; rely on `.claude/` plus a small
   `copilot-instructions.md` stub pointing at `CLAUDE.md` for anyone who does run
   Copilot against the repo.

## Decision

Adopt option 3: **Claude is the single agent harness**.

- **Removed** — `.github/agents/`, `.github/instructions/`, `.github/prompts/`. The 27
  files in those trees were the Copilot-format agents, instructions, prompts, and shared
  guides, plus the `REFACTORING_SUMMARY.md` / `COPILOT_ARCHITECTURE.md` /
  `CONTEXT_INVESTIGATION.md` meta-docs about the harness itself.
- **Slimmed** — `.github/copilot-instructions.md` is now a short stub that points at
  `CLAUDE.md`, `AGENT_WORKFLOW.md`, `docs/api-facts.yaml`, and `docs/adr/`. GitHub
  Copilot users get the canonical guidance; there is no parallel set of docs to
  maintain.
- **Kept** — `.claude/agents/`, `.claude/skills/`, `.claude/hooks/`, the `frontapp` MCP
  server, and the inline guidance in `CLAUDE.md` and `AGENT_WORKFLOW.md`. These are the
  active surface and have been kept current per the user's "AI-agent-first repo"
  principle.

This ADR supersedes ADR-0014. The three-tier `.github/agents/` architecture is no longer
in use.

## Consequences

### Positive

1. **No drift surface** — there's only one harness to keep current. Every PR that
   adjusts a pattern updates one place (CLAUDE.md, `.claude/`) instead of two.
2. **Reduced maintenance** — ~7,300 lines of inherited template are no longer pretending
   to be canonical. New contributors don't waste time reading them.
3. **Aligns with actual usage** — the recent vertical-shipping cadence proves the Claude
   harness is what's load-bearing. Removing the parallel harness reflects reality.
4. **GitHub Copilot still works** — anyone running Copilot picks up
   `copilot-instructions.md`, which points at the same canonical guidance the Claude
   harness uses. Copilot inherits the same architecture overview, validation tiers,
   commit standards, and anti-patterns from CLAUDE.md.
5. **No more "is this updated?" question** — when a new vertical ships and
   `.claude/agents/vertical-planner.md` learns a new pattern, there isn't a sibling
   `python-developer.agent.md` that needs the same edit.

### Negative

1. **Loss of file-pattern auto-applying instructions** — `.github/instructions/*.md`
   with `applyTo: "**/*.py"` automatically pulled into Copilot's context for every
   Python file edit. The replacement (`copilot-instructions.md` referencing CLAUDE.md)
   loads on every interaction but isn't pattern-scoped. Acceptable: the project's
   anti-pattern list in CLAUDE.md is short enough to live in the global instructions.
2. **Loss of role-specific Copilot agents** — `@python-developer`, `@tdd-specialist`,
   etc. no longer exist. Anyone wanting role-specialized agents inside Copilot has to
   define their own. Acceptable: the Claude harness has equivalents (`vertical-planner`,
   `domain-advisor`, `code-modernizer`, `pr-preparer`, `spec-auditor`) and
   slash-commands (`/review`, `/techdebt`, `/write-tests`, `/verify`).
3. **Reversibility cost** — if a future contributor wants the Copilot harness back, they
   have to rebuild it from scratch (or restore from git history). The git history is
   preserved, so this is annoying but not blocking.

### Neutral

1. **`.github/copilot-instructions.md` is the only Copilot surface** — kept short (under
   50 lines) so it doesn't drift. Anything substantial points at CLAUDE.md.
2. **CODEOWNERS, ISSUE_TEMPLATE, pull_request_template, dependabot, FUNDING, workflows**
   under `.github/` are unaffected — those are GitHub-platform concerns (PR templates,
   dependency bots, CI), not part of the agent harness.

## Alternatives considered

### Keep + rewrite the Copilot harness with Front-domain examples

Replace every `purchase_order` / `inventory` / `sku` reference with `conversation` /
`tag` / `contact_id`. Update agent definitions to reference real `.agent.md` filenames.
Re-fact-check the `100+ endpoints` numbers.

**Rejected**: estimated several hours of pure docs work with no concrete user, and the
maintenance bill recurs every time the patterns evolve. The drift detected under PR #30
/ issue #39 would just resurface in six months. This option also doesn't address the
deeper structural problem flagged in issue #32 — even project-coordinator.agent.md and
task-planner.agent.md describe orchestration patterns that aren't actually in use.

### Keep + freeze the Copilot harness

Mark all the `.github/agents/` files as "do not maintain" and let them rot explicitly.

**Rejected**: rotting docs are a liability, especially when they appear authoritative
(YAML frontmatter, `.agent.md` extension). Future contributors would discover them, read
them, and waste time on outdated patterns. Worse, AI agents indexing the repo would
surface them as if current.

### Migrate to a different cross-runtime harness format (.cursor, awesome-copilot)

Move to a format that more cross-runtimes can consume.

**Rejected**: same drift problem with a different file extension. Cross-runtime support
requires every runtime to actually use the files; we don't have evidence of that for any
format. Single-source-of-truth via CLAUDE.md is the simplest backstop.

## Implementation notes

### What was removed

```
.github/agents/                                # 7 *.agent.md files + guides/
.github/instructions/                          # 4 *.instructions.md files
.github/prompts/                               # 5 *.prompt.md files
```

### What was updated

- `.github/copilot-instructions.md` — slimmed from ~400 lines to a short stub pointing
  at CLAUDE.md, AGENT_WORKFLOW.md, `docs/api-facts.yaml`, and `docs/adr/`.
- `CLAUDE.md` "Detailed Documentation" table — removed rows that pointed at
  `.github/agents/guides/shared/*.md`. Added a note that validation tiers, commit
  standards, and file rules are documented inline in CLAUDE.md.
- `AGENT_WORKFLOW.md` "Detailed references" — removed references to deleted
  `.github/agents/guides/shared/*.md` files.
- ADR-0014 — marked as Superseded by this ADR.

### What was kept

- `.claude/agents/` — the active sub-agent definitions (vertical-planner,
  domain-advisor, code-modernizer, pr-preparer, spec-auditor).
- `.claude/skills/` — the active workflow skills (new-vertical, vendor-and-regen,
  open-pr, review-pr, babysit-prs).
- `.claude/hooks/` — block-generated-edits, format-on-edit.
- `.claude/commands/` — verify, review, techdebt, write-tests, generate-docs,
  pre-commit.
- `.github/copilot-instructions.md` — slim stub, see above.
- `.github/CODEOWNERS`, `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`,
  `.github/dependabot.yml`, `.github/FUNDING.yml`, `.github/workflows/` — GitHub
  platform concerns; unaffected.

### If GitHub Copilot is enabled

The slim `.github/copilot-instructions.md` ships every Copilot session with the
canonical guidance from `CLAUDE.md`. Anyone running Copilot against this repo gets the
same architecture overview, validation tier guidance, generated-file rules, and
conventional-commit format that Claude Code sees.

## References

- Issue #17 — original harness audit that flagged the StatusPro residue
- Issue #32 — coordinator + planner agents describing non-existent dual-harness reality
- Issue #39 — full StatusPro-residue audit of `.github/`
- ADR-0014 — the original Copilot harness decision (now superseded)
- `CLAUDE.md` — canonical project guidance
- `AGENT_WORKFLOW.md` — step-by-step walkthrough
- `docs/api-facts.yaml` — generated API facts index
