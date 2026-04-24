# ADR-009: Use uv as the Package Manager

## Status

Accepted

Date: 2026-04-24

## Context

The Frontapp OpenAPI Client adopted **uv** as the Python package and dependency manager
from day one. This ADR captures the rationale so contributors coming from Poetry-based
projects understand the choice.

### Current state

- **Package manager**: uv (Astral)
- **Build backend**: hatchling
- **Task runner**: poethepoet (poe)
- **Dependencies**: ~15 core + ~10 dev dependencies + docs group + MCP server workspace
  member
- **Python versions**: 3.12, 3.13, 3.14
- **Configuration**: PEP 621-compliant `pyproject.toml` + `[tool.uv.*]` sections for
  workspace config

### Forces at play

**Performance**:

- uv dependency resolution is 10-100× faster than pip / Poetry for typical dependency
  graphs, written in Rust
- Lockfile generation takes seconds instead of minutes
- CI/CD install steps are a fraction of what they'd be with Poetry

**Tool consolidation**:

- uv replaces `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, and `virtualenv`
  in a single binary
- Reduces toolchain complexity for contributors
- Native support for PEP 621 pyproject.toml layout
- First-class workspace support (we use this for the `frontapp-mcp-server` workspace
  member under the same lockfile as `frontapp-openapi-client`)

**Ecosystem alignment**:

- uv has become the default modern Python package manager in 2026
- Actively maintained by Astral (creators of ruff, which we also use)
- Growing adoption across OSS Python projects

**Standards compliance**:

- Strict PEP 517/518/621 compliance
- No vendor-specific lockfile or metadata sections
- Switching to a different PEP 517-compliant tool later is a one-file change

## Decision

Use **uv** as the primary package and dependency manager. Specifically:

1. **Dependency management**: `uv sync`, `uv add`, `uv remove`, `uv lock`
2. **Build backend**: `hatchling` (in the `[build-system]` section) — simple, PEP
   517-compliant, and maintained alongside uv by Astral
3. **Task runner**: continue using `poethepoet`, invoked as `uv run poe ...`
4. **Lockfile**: `uv.lock` committed at the workspace root
5. **Workspace layout**: single `uv.lock` for the whole monorepo, `[tool.uv.workspace]`
   lists `frontapp_mcp_server` as a member

## Consequences

### Positive

- **Fast iteration**: dependency operations are near-instantaneous
- **Fast CI**: `uv sync` in CI is seconds, not minutes
- **One tool**: no more jumping between pip, pip-tools, pyenv, twine, etc.
- **Workspace-native**: the monorepo shape (client + MCP server under one lockfile)
  works out of the box — no extension plugins needed
- **Ruff-compatible workflow**: uv and ruff are both from Astral; the tooling story is
  coherent end-to-end
- **Standard `pyproject.toml`**: no vendor-specific sections means migrating away later
  (if ever) is low-risk
- **Rust-speed installs**: contributors feel the difference immediately on first
  `uv sync`

### Negative

- **Newer tool**: less battle-tested than Poetry for corner cases. Mitigation: we're
  already past the early-adopter phase in 2026; Astral's release cadence is measured
- **Learning curve**: contributors coming from Poetry need to learn new commands.
  Mitigation: the commands are small (`uv sync`, `uv add`, `uv run`) and documented in
  the README
- **Different lockfile format**: `uv.lock` ≠ `poetry.lock`. Mitigation: this project
  only targets uv; there's no dual-lockfile burden

### Neutral

- **Still using poe for tasks**: `uv run poe <task>` is one more keyword than
  `poe <task>`, but the `uv run` prefix makes the venv-activation implicit and keeps the
  command portable across environments

## Alternatives considered

### Stay with Poetry

**Rejected**: slower performance; non-standard `[tool.poetry]` sections in
`pyproject.toml` make downstream compatibility awkward; ecosystem momentum has shifted
to uv.

### PDM

An alternative modern Python package manager.

**Pros**: better than Poetry on performance; standards-compliant; decent workspace
support.

**Cons**: smaller ecosystem; slower than uv; would require a second migration later if
uv continues to dominate.

**Rejected**: if we're switching from the default (Poetry), uv is the destination worth
investing in.

### pip + pip-tools + venv

Raw pip with external lockfile management.

**Pros**: maximum flexibility; no new tool to learn.

**Cons**: separate tools for every concern (resolution, installation, build, publish);
slow; no workspace support.

**Rejected**: complexity without the upside uv provides.

## References

- [uv documentation](https://docs.astral.sh/uv/)
- [Astral blog — announcing uv](https://astral.sh/blog/uv)
- [PEP 621 — Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [ADR-0012: Validation Tiers for Agent Workflows](../../frontapp_public_api_client/docs/adr/0012-validation-tiers-for-agent-workflows.md)
  — uv's speed enables the quick-check tier
