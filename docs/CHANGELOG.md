# CHANGELOG

<!-- version list -->

## v0.1.0 (unreleased)

Initial monorepo for the Frontapp API client ecosystem:

- `frontapp-openapi-client` — Python client for Front's Core API with
  transport-layer retries, rate-limit awareness, and domain helpers
  (`client.conversations.…` vertical live today).
- `frontapp-mcp-server` — FastMCP server exposing 8 conversation tools
  (5 read-only, 3 mutations with two-step confirm + `ctx.elicit`).
- `frontapp-client` — TypeScript client generated from the same spec via
  `@hey-api/openapi-ts`, layered with resilient-fetch + pagination
  middleware.
