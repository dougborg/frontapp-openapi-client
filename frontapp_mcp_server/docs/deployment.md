# MCP Server Deployment Guide

This document describes how the Frontapp MCP Server is released and published to PyPI.
For the full mechanics (release-please, the release PR, tag-triggered publishing), see
[docs/RELEASE.md](https://github.com/dougborg/frontapp-openapi-client/blob/main/docs/RELEASE.md) -
this page covers what's specific to the MCP package.

## How Releases Work

Releases are automated using **release-please** in manifest mode, one aggregated release
PR per set of changes across all three packages in this repo. In short:

1. Commits touching `frontapp_mcp_server/` accumulate on release-please's release PR,
   which bumps `frontapp_mcp_server/pyproject.toml`'s version and updates
   `frontapp_mcp_server/CHANGELOG.md`
1. Merging that PR creates the `mcp-v{version}` tag and a **draft** GitHub Release at
   the merge commit
1. The tag push triggers `.github/workflows/publish.yml`'s `publish-mcp` job, which
   builds the package, publishes to PyPI via OIDC, attaches the build artifacts to the
   draft release, and publishes the release
1. `publish-mcp-docker` then builds and pushes a multi-arch image to
   `ghcr.io/dougborg/frontapp-mcp-server`

Which commit types bump the version:

| Commit Type | Example                    | Release? | Version Bump        |
| ----------- | -------------------------- | -------- | ------------------- |
| `feat`      | Add new order tool         | ✅       | MINOR (0.1.0→0.2.0) |
| `fix`       | Fix auth error             | ✅       | PATCH (0.1.0→0.1.1) |
| `perf`      | Optimize query performance | ✅       | PATCH (0.1.0→0.1.1) |
| `feat!`     | Breaking API change        | ✅       | MAJOR (0.1.0→1.0.0) |
| `docs`      | Update documentation       | ❌       | No release          |
| `test`      | Add unit tests             | ❌       | No release          |
| `chore`     | Update dependencies        | ❌       | No release          |

Unlike the old per-package semantic-release setup, whether a commit bumps the MCP
package no longer depends on a `(mcp)` commit _scope_ - it depends on whether the commit
**touches files under `frontapp_mcp_server/`**. A `(mcp)` scope is still good practice
for changelog readability, but it isn't load-bearing anymore.

## Verify a Release

After a release is published (check
[GitHub Releases](https://github.com/dougborg/frontapp-openapi-client/releases)):

### 1. Check PyPI Page

Visit: https://pypi.org/project/frontapp-mcp-server/

Verify:

- ✅ New version is listed
- ✅ README renders correctly
- ✅ Project metadata is correct
- ✅ Installation command works

### 2. Test Installation from PyPI

```bash
# Create fresh test environment
cd /tmp
python3 -m venv test-pypi-install
source test-pypi-install/bin/activate

# Install from PyPI
pip install frontapp-mcp-server

# Verify installation
pip list | grep frontapp

# Test command (should require API key)
frontapp-mcp-server
# Expected: "FRONTAPP_API_KEY environment variable is required"

# Clean up
deactivate
rm -rf /tmp/test-pypi-install
```

### 3. Test with Claude Desktop

Update Claude Desktop config
(`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "frontapp": {
      "command": "uvx",
      "args": ["frontapp-mcp-server"],
      "env": {
        "FRONTAPP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Restart Claude Desktop and verify:

- ✅ Server starts without errors
- ✅ Inventory tools appear in MCP tools list
- ✅ Tools work when invoked

## Manual Testing Before Release

Before merging a PR that will trigger a release, test locally:

### Run All Tests

```bash
cd frontapp_mcp_server

# Unit tests (fast)
uv run pytest tests/ -m "not integration"

# Integration tests (requires FRONTAPP_API_KEY in .env)
uv run pytest tests/ -m integration

# All tests
uv run pytest tests/
```

### Test Local Build

```bash
cd frontapp_mcp_server

# Build package
uv build

# Install locally (in a test venv)
cd /tmp
python3 -m venv test-local
source test-local/bin/activate
pip install /path/to/frontapp-openapi-client/frontapp_mcp_server/dist/*.whl

# Test
frontapp-mcp-server --help

# Clean up
deactivate
rm -rf /tmp/test-local
```

## If a Release or Publish Fails

See the Troubleshooting section of
[docs/RELEASE.md](https://github.com/dougborg/frontapp-openapi-client/blob/main/docs/RELEASE.md#troubleshooting)
for the general flow. The most common MCP-specific case: the `publish-mcp` job fails its
PyPI-publish step because the PyPI Trusted Publisher for `frontapp-mcp-server` (workflow
`publish.yml`, job `publish-mcp`) hasn't been configured yet. Configure it, then re-run
the failed workflow run - the tag and draft release already exist, so publishing picks
up from there without creating a duplicate.

## PyPI Trusted Publisher

To be configured at:
https://pypi.org/manage/project/frontapp-mcp-server/settings/publishing/

- **Owner**: `dougborg`
- **Repository**: `frontapp-openapi-client`
- **Workflow**: `publish.yml`
- **Job**: `publish-mcp`
- **Environment**: `pypi-mcp`

## Version Numbering

This project uses semantic versioning with pre-release identifiers:

### Version Format: `MAJOR.MINOR.PATCH[-prerelease]`

- **MAJOR**: Breaking changes (`feat!:` or `BREAKING CHANGE:` touching
  `frontapp_mcp_server/`)
- **MINOR**: New features (`feat:` touching `frontapp_mcp_server/`)
- **PATCH**: Bug fixes (`fix:`, `perf:` touching `frontapp_mcp_server/`)

### Pre-release Phases:

- **Alpha** (0.1.0a1, 0.1.0a2): Early development, unstable, breaking changes expected
- **Beta** (0.1.0b1): Feature complete, testing, API stabilizing
- **RC** (0.1.0rc1): Release candidate, final testing
- **Stable** (0.1.0, 1.0.0): Production-ready release

**Current Phase**: Alpha - API may change between versions

## Checklist for Contributors

Before submitting a PR that will trigger a release:

- [ ] All tests pass locally: `uv run pytest tests/`
- [ ] Commit messages follow conventional commits
- [ ] README updated if adding new features
- [ ] Integration tests added/updated if needed
- [ ] Breaking changes documented in commit body (if any)

After the release PR is merged:

- [ ] Check GitHub Actions for a successful `publish.yml` run
- [ ] Verify new version on PyPI
- [ ] Test installation from PyPI
- [ ] Check GitHub Release notes

## Related Documentation

- **Release Process**:
  [docs/RELEASE.md](https://github.com/dougborg/frontapp-openapi-client/blob/main/docs/RELEASE.md) -
  Full release-please flow across all three packages
- **Contributing**:
  [docs/CONTRIBUTING.md](https://github.com/dougborg/frontapp-openapi-client/blob/main/docs/CONTRIBUTING.md) -
  Commit message format
- **MCP Documentation Index**:
  [frontapp_mcp_server/docs/index.md](https://github.com/dougborg/frontapp-openapi-client/blob/main/frontapp_mcp_server/docs/index.md) -
  All MCP documentation

## Related Links

- **PyPI Project**: https://pypi.org/project/frontapp-mcp-server/
- **GitHub Repository**: https://github.com/dougborg/frontapp-openapi-client
- **GitHub Releases**:
  https://github.com/dougborg/frontapp-openapi-client/releases?q=mcp-v
- **Main Client**: https://pypi.org/project/frontapp-openapi-client/
