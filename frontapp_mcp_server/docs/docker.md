# Docker MCP Server Guide

This guide covers building, testing, and submitting the Frontapp MCP Server to the
Docker MCP Catalog.

## Pre-built Images

Pre-built multi-platform (amd64/arm64) images are automatically published to GitHub
Container Registry on each release:

```bash
# Pull the latest version
docker pull ghcr.io/dougborg/frontapp-mcp-server:latest

# Or pull a specific version
docker pull ghcr.io/dougborg/frontapp-mcp-server:0.1.0
```

## Building the Docker Image

### Local Build

```bash
cd frontapp_mcp_server
docker build -t frontapp-mcp-server:latest .
```

### Multi-platform Build (for registry)

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t your-registry/frontapp-mcp-server:latest \
  --push .
```

## Transport Modes

The Docker image supports multiple transport modes. The default is `streamable-http`,
which serves HTTP on port 8765.

| Transport         | Default      | Use Case                           |
| ----------------- | ------------ | ---------------------------------- |
| `streamable-http` | Yes (Docker) | Claude.ai co-work, remote clients  |
| `stdio`           | No           | Claude Desktop, Docker MCP Catalog |
| `sse`             | No           | Cursor IDE                         |

Override the transport by replacing the `CMD` arguments:

```bash
# HTTP (default) — no override needed
docker run -p 8765:8765 -e FRONTAPP_API_KEY=your-key frontapp-mcp-server:latest

# stdio — for Claude Desktop
docker run -it -e FRONTAPP_API_KEY=your-key frontapp-mcp-server:latest --transport stdio

# SSE — for Cursor IDE
docker run -p 8765:8765 -e FRONTAPP_API_KEY=your-key frontapp-mcp-server:latest \
  --transport sse --host 0.0.0.0 --port 8765
```

## Running Locally

### Using Docker Compose (recommended)

```bash
cd frontapp_mcp_server

# Configure your API key
cp .env.example .env
# Edit .env and set FRONTAPP_API_KEY

# Start the server (HTTP on port 8765)
docker compose up
```

Or from the repo root, pointing at the compose file:

```bash
docker compose -f frontapp_mcp_server/docker-compose.yml up
```

The server starts on `http://localhost:8765/mcp` with a health check and automatic
restart.

### Using Docker Run

```bash
# HTTP transport (for Claude.ai co-work / remote access)
docker run -p 8765:8765 \
  -e FRONTAPP_API_KEY="your-api-key-here" \
  ghcr.io/dougborg/frontapp-mcp-server:latest

# stdio transport (for Claude Desktop)
docker run -it \
  -e FRONTAPP_API_KEY="your-api-key-here" \
  ghcr.io/dougborg/frontapp-mcp-server:latest --transport stdio
```

## Testing the Container

```bash
# Start the server
docker run -p 8765:8765 \
  -e FRONTAPP_API_KEY="your-api-key-here" \
  ghcr.io/dougborg/frontapp-mcp-server:latest

# Should show:
# - Server initialization logs
# - Ready message
# - Listening on http://0.0.0.0:8765/mcp

# Verify the endpoint is reachable
curl http://localhost:8765/mcp
```

## Docker MCP Catalog Submission

### Prerequisites

1. **GitHub Repository**: Code must be in a public GitHub repository
1. **Working Dockerfile**: Tested and verified locally
1. **Documentation**: README with clear setup instructions
1. **License**: Open source license (MIT in our case)

### Generating Tool Metadata

To generate `tools.json` for Docker MCP Registry submission:

```bash
# Generate to stdout
python scripts/generate_tools_json.py

# Generate to file
python scripts/generate_tools_json.py -o tools.json

# Generate with pretty formatting
python scripts/generate_tools_json.py -o tools.json --pretty
```

The script automatically introspects the FastMCP server to extract tool metadata,
ensuring the tools list stays synchronized with actual implementations.

#### Example Output

```json
[
  {
    "name": "list_conversations",
    "description": "List Front conversations with Front search syntax."
  },
  {
    "name": "update_conversation",
    "description": "Archive, reassign, or retag a conversation (two-step confirm)."
  },
  {
    "name": "reply_to_conversation",
    "description": "Send an outbound reply to the customer (two-step confirm)."
  }
]
```

#### CI/CD Integration

The script can be run in CI/CD to verify tool metadata is accurate:

```yaml
# In .github/workflows/ci.yml
- name: Generate tools.json
  run: python scripts/generate_tools_json.py -o tools.json --pretty

- name: Verify tools.json is up to date
  run: |
    git diff --exit-code tools.json || {
      echo "tools.json is out of date. Run: python scripts/generate_tools_json.py -o tools.json --pretty"
      exit 1
    }
```

### Submission Process

1. **Fork the MCP Registry**: https://github.com/docker/mcp-registry

1. **Create Submission File**: Add `frontapp-mcp-server.yml` to the registry

1. **Submit Pull Request**: Follow the CONTRIBUTING guide

### Recommended Approach: Docker-Built

We recommend the **Docker-built** option because:

- ✅ Docker builds and signs the image
- ✅ Automatic security scanning and updates
- ✅ Provenance tracking and SBOMs
- ✅ Published to `mcp/frontapp-mcp-server` namespace

### Submission File Format

```yaml
name: frontapp-mcp-server
title: Frontapp Manufacturing ERP
description: MCP server for interacting with Frontapp Manufacturing ERP API
repository: https://github.com/dougborg/frontapp-openapi-client
dockerfile_path: frontapp_mcp_server/Dockerfile
version: 0.1.0
license: MIT
author: Doug Borg
tags:
  - conversations
  - erp
  - statuses
  - conversations
categories:
  - business
  - conversations
build_type: docker-built # Docker will build and maintain
```

## Configuration Examples

### Claude Desktop (stdio via Docker)

```json
{
  "mcpServers": {
    "frontapp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "FRONTAPP_API_KEY=your-key-here",
        "mcp/frontapp-mcp-server:latest",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

### Claude.ai Co-work (streamable-http via Docker)

```bash
# Start the server
docker run -p 8765:8765 -e FRONTAPP_API_KEY=your-key-here \
  ghcr.io/dougborg/frontapp-mcp-server:latest

# Then in Claude.ai: Customize > Connectors > Add custom connector
# Enter: http://your-host:8765/mcp
```

For local development, use a tunnel to expose the server:

```bash
ngrok http 8765
# Use the ngrok URL as your connector URL in Claude.ai
```

## Security Considerations

- ✅ Non-root user (UID 1000)
- ✅ Minimal base image (python:3.14-slim)
- ✅ No unnecessary packages
- ✅ API key passed via environment variable (never hardcoded)
- ✅ Resource limits in docker-compose

## Timeline

- **Submission**: Create PR in mcp-registry
- **Review**: Docker team reviews (typically 1-2 days)
- **Approval**: Available within 24 hours of approval
- **Availability**:
  - Docker MCP Catalog _(link pending official catalog launch)_
  - Docker Desktop MCP Toolkit
  - One-click connection in Claude Desktop

## Resources

- [MCP Registry GitHub](https://github.com/docker/mcp-registry)
- [Docker MCP Documentation](https://docs.docker.com/ai/mcp-catalog-and-toolkit/)
- Docker MCP Catalog _(URL will be provided when officially available)_
