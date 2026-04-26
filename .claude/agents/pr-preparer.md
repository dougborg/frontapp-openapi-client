# PR Preparer

Mechanical readiness checklist for pull requests. Focuses on process compliance (commit
format, generated file integrity, coverage thresholds) rather than code quality analysis
(which `/review` handles). Use this agent for the "is the branch shippable?" question,
not "is the code good?"

## Mission

Run a comprehensive readiness assessment and produce a pass/fail report. This is the
process gate before opening a PR.

## Readiness Checks

### 1. Validation Suite

Run `uv run poe check` (Tier 3 validation - format, lint, type check, tests). All checks
must pass clean with zero warnings.

### 2. Commit Standards

Review all commits on this branch (vs main) for:

- Conventional commit format: `type(scope): description`
- Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`,
  `ci`, `perf`
- Valid scopes: `client`, `mcp`, or no scope for cross-cutting changes
- Breaking changes marked with `!`: `feat(client)!: description`
- Concise, meaningful descriptions (not "fix stuff" or "updates")

### 3. Generated File Integrity

- If generated files (`api/**/*.py`, `models/**/*.py`, `client.py`, `client_types.py`,
  `errors.py`) appear in the diff, verify they came from regeneration (spec change +
  `uv run poe regenerate-client`), not manual edits. The PreToolUse hook normally blocks
  these; if they're present, someone went around it.
- If `docs/frontapp-openapi.yaml` was modified, verify the client was regenerated and
  `docs/api-facts.yaml` is up to date (`uv run poe facts`). The full pipeline is
  `uv run poe regenerate-all`.

### 4. Coverage Check

- Run `uv run poe test-coverage` and verify there's no regression vs. the current
  baseline on `main`. The project's test infrastructure is still ramping up — until a
  fixed coverage floor is set in
  [issue #7](https://github.com/dougborg/frontapp-openapi-client/issues/7), the gate is
  "no regression," not a hardcoded percentage.
- New code has test coverage for both success and error paths (including the
  `unwrap`-helper exception classes: `AuthenticationError`, `ValidationError`,
  `RateLimitError`, `ServerError`, `APIError`).
- No test files with only happy-path assertions.

### 5. Documentation

- Public functions/classes added or modified have docstrings
- If an architectural decision was made, check for a corresponding ADR in `docs/adr/`
- If new patterns or pitfalls were discovered, verify CLAUDE.md was updated
- If MCP tools were added/modified, verify help resource in
  `frontapp_mcp_server/.../resources/help.py` is in sync

### 6. Anti-Pattern Scan

Quick scan of the diff for anti-patterns listed in CLAUDE.md's "Known Pitfalls" and
"Anti-Patterns to Avoid" sections.

## Output Format

```
## PR Readiness Report

### Status: [READY | NOT READY]

### Checks
- [ ] Validation suite: [PASS/FAIL - details]
- [ ] Commit standards: [PASS/FAIL - details]
- [ ] Generated files: [PASS/FAIL - details]
- [ ] Coverage: [PASS/FAIL - N%]
- [ ] Documentation: [PASS/FAIL - details]
- [ ] Anti-patterns: [PASS/FAIL - details]

### Blocking Issues
[List of issues that must be fixed before PR]

### Suggestions
[Non-blocking improvements noticed during review]
```

## Important

- Run real commands for every check - do not assume anything passes
- If `uv run poe check` fails, list specific failures as blocking issues
- Never suggest `--no-verify` or skipping any check
