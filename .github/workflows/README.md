# GitHub Actions Workflows

This directory contains the CI/CD workflows for the Frontapp OpenAPI Client project.

## Workflows

### [ci.yml](ci.yml)

**Trigger:** Pull requests to `main` branch

**Purpose:** Continuous integration checks for pull requests

**Steps:**

- Install dependencies with uv
- Run full CI pipeline (`uv run poe ci`)
  - Format checking
  - Linting (ruff, mypy, yamllint)
  - Tests with coverage
  - OpenAPI validation

**Permissions:** `contents: read`

### [docs.yml](docs.yml)

**Trigger:**

- Push to `main` branch (when docs-related files change)
- Manual workflow dispatch

**Purpose:** Build and deploy documentation to GitHub Pages

**Steps:**

- Build MkDocs documentation
- Upload documentation artifacts
- Deploy to GitHub Pages

**Permissions:** `contents: read`, `pages: write`, `id-token: write`

**Note:** This workflow only runs when documentation files change (docs/\*\*,
mkdocs.yml, etc.) to avoid unnecessary builds.

### [release-please.yml](release-please.yml)

**Trigger:** Push to `main` branch

**Purpose:** The only workflow that watches `main` for release purposes. Opens or
updates **one aggregated release PR** covering all three packages
(`separate-pull-requests: false` in `release-please-config.json`); once that PR is
merged, creates a tag + draft GitHub Release per changed package
(`client-v*`/`mcp-v*`/`ts-v*`) at the merge commit. Never pushes to `main` itself.

**Permissions:** `contents: write`, `pull-requests: write`

**Note:** See [docs/RELEASE.md](../../docs/RELEASE.md) for the full flow. Configuration:
[`release-please-config.json`](../../release-please-config.json) and
[`.release-please-manifest.json`](../../.release-please-manifest.json) at the repo root.

### [release-pr-prepare.yml](release-pr-prepare.yml)

**Trigger:** `pull_request` (opened/synchronize/reopened) against `main`, filtered to
release-please's own branch (`release-please--*`)

**Purpose:** Glue that keeps the release PR internally consistent - resyncs `uv.lock` to
the versions release-please just bumped, and keeps
`frontapp_mcp_server/pyproject.toml`'s `frontapp-openapi-client>=X` floor equal to the
client version the PR proposes (fixes #165, and keeps it fixed going forward). Both land
as a commit on the release PR branch, never on `main`.

**Permissions:** `contents: write`

### [publish.yml](publish.yml)

**Trigger:** Push of a `client-v*`, `mcp-v*`, or `ts-v*` tag - i.e. only after a
release-please release PR merges. Never triggered by a `main` push.

**Purpose:** The only workflow that builds and ships artifacts.

**Jobs:**

1. **publish-client** (`client-v*`): build with `uv build`, publish to PyPI via OIDC,
   attach dist artifacts to the still-draft release, publish the release
1. **publish-mcp** (`mcp-v*`): same, for the MCP server package
1. **publish-mcp-docker** (`mcp-v*`, needs `publish-mcp`): build and push a multi-arch
   image to `ghcr.io/dougborg/frontapp-mcp-server`
1. **publish-ts** (`ts-v*`): build with `pnpm`, publish to npm via OIDC, attach the
   packed tarball to the still-draft release, publish the release

Each publish job builds its assets and publishes to the registry **before** attaching
assets to the release and flipping it out of draft - draft releases accept asset
uploads, published releases are
[immutable](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)
and permanently reject them.

**Permissions:** `id-token: write` + `contents: write` per publish-\* job;
`contents: read` + `packages: write` for `publish-mcp-docker`

**Prerequisite:** PyPI Trusted Publishers for `frontapp-openapi-client` and
`frontapp-mcp-server`, and an npm Trusted Publisher for `frontapp-client`, must be
registered before these jobs can succeed - see
[docs/RELEASE.md](../../docs/RELEASE.md#manual-prerequisites-before-the-first-real-release).

### [security.yml](security.yml)

**Trigger:** Weekly schedule (Sundays at 00:00 UTC)

**Purpose:** Security scanning and dependency audits

**Steps:**

- Dependency vulnerability scanning
- Code security analysis
- License compliance checks

**Permissions:** `contents: read`, `security-events: write`

### [copilot-setup-steps.yml](copilot-setup-steps.yml)

**Type:** Reusable workflow

**Purpose:** Common setup steps for GitHub Copilot integrations

**Provides:**

- Dependency installation
- Environment configuration
- Caching setup

## Workflow Orchestration

```mermaid
graph TD
    A[Push to main] --> B[CI checks]
    A --> C[release-please.yml]
    A --> D[Docs workflow]

    C --> E{Release-worthy commits since last release?}
    E -->|Yes| F[Open/update aggregated release PR]
    E -->|Release PR just merged| G[Create tags + draft Releases]
    E -->|No| H[No-op]

    G --> I[client-v* tag]
    G --> J[mcp-v* tag]
    G --> K[ts-v* tag]

    I --> L[publish.yml: publish-client]
    J --> M[publish.yml: publish-mcp]
    K --> N[publish.yml: publish-ts]

    M --> O[publish.yml: publish-mcp-docker]

    F --> P[release-pr-prepare.yml]
    P --> Q[uv.lock + MCP client pin synced on PR branch]

    D --> R{Docs changed?}
    R -->|Yes| S[Build & Deploy]
    R -->|No| T[Skip]

    style A fill:#e1f5ff
    style F fill:#fff3cd
    style G fill:#d4edda
    style L fill:#d4edda
    style M fill:#d4edda
    style N fill:#d4edda
    style O fill:#d4edda
    style S fill:#d4edda
```

## Configuration

### Secrets and Variables Required

- `GITHUB_TOKEN` - Automatically provided by GitHub Actions
- `vars.RELEASE_PLEASE_APP_ID` / `secrets.RELEASE_PLEASE_APP_PRIVATE_KEY` - GitHub App
  credentials for the `dougborg-release-please` App (ID 4392719), used to open/update
  the release PR and to push the `uv.lock`/MCP-pin sync commit to it
- PyPI/npm publishing uses Trusted Publishers (OIDC) - no manual tokens. **Not yet
  registered** for any of the three packages; see
  [docs/RELEASE.md](../../docs/RELEASE.md#manual-prerequisites-before-the-first-real-release)

### Environments

`publish.yml` scopes each registry publish to a GitHub Environment (`pypi-client`,
`pypi-mcp`, `npm-ts`) - the recommended way to scope OIDC trust for Trusted Publishing.
These aren't required to exist for the workflow YAML to be valid; GitHub creates an
environment automatically the first time a job references it.

## Local Testing

Test workflows locally using [act](https://github.com/nektos/act):

```bash
# Test CI workflow
act pull_request -W .github/workflows/ci.yml

# Test docs build (without deploy)
act workflow_dispatch -W .github/workflows/docs.yml
```

`release-please.yml` and `publish.yml` are not practical to run under `act` - they
depend on the GitHub App token minting action and, for `publish.yml`, on OIDC-based
registry auth that only works inside real GitHub Actions runs.

## Maintenance

### Updating Actions

Keep actions up to date by:

1. Monitoring Dependabot alerts
1. Reviewing action changelogs
1. Testing in a branch before merging

### Adding New Workflows

When adding new workflows:

1. Create the workflow file
1. Update this README
1. Test locally with `act` where practical
1. Create a PR for review
1. Update branch protection rules if needed

## Troubleshooting

See [docs/RELEASE.md](../../docs/RELEASE.md#troubleshooting) for release-specific
troubleshooting (no release PR appearing, stale `uv.lock`/pin, publish auth failures,
releases stuck in draft).

**Docs not deploying:**

- Check that `docs/**` files were actually changed
- Verify GitHub Pages is enabled in repository settings
- Check workflow logs for build errors

### Debug Mode

Enable workflow debug logging:

```bash
# In repository settings > Secrets and variables > Actions
# Add repository secret:
ACTIONS_STEP_DEBUG=true
ACTIONS_RUNNER_DEBUG=true
```

## Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://docs.astral.sh/uv/)
- [release-please](https://github.com/googleapis/release-please)
- [MkDocs](https://www.mkdocs.org/)
