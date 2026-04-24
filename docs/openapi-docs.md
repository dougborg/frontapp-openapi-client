# OpenAPI Documentation

This page renders the complete OpenAPI specification for Front's
[Core API](https://dev.frontapp.com/reference/introduction) using Swagger UI for
interactive exploration. The spec is vendored from
[frontapp/front-api-specs](https://github.com/frontapp/front-api-specs) and sanitized by
`scripts/vendor_spec.py`.

## About the Front API

Front is a shared-inbox customer-communication platform. The Core API exposes:

- **Conversations** — email/SMS/chat threads, with status, assignment, tags, and full
  message history
- **Messages** — individual messages inside conversations
- **Comments** — internal teammate-only notes on conversations
- **Contacts** — external parties, their handles (emails/phones), and notes
- **Teammates & Teams** — workspace users and their inbox access
- **Tags & Inboxes** — workspace organization primitives
- **Channels** — custom integrations for syncing messages from external systems
- **Rules, Signatures, Message Templates, Drafts, Analytics, Knowledge Base, Custom
  Fields, Webhooks** — full workspace management surface

## Interactive API Explorer

Use the interactive explorer below to:

- **Browse endpoints** organized by tag
- **View request/response schemas** with detailed type information
- **Test API calls** directly from the documentation (with proper authentication)
- **Explore examples** for each endpoint

!!! tip "API Authentication" To test API calls:

    1. Click the **Authorize** button in the Swagger UI below
    2. Enter your token in the format `Bearer YOUR_TOKEN`
    3. Get a token at Front → Settings → Developers → API tokens

!!! info "Base URL" Production: `https://api2.frontapp.com`

---

<swagger-ui src="frontapp-openapi.yaml"/>

## Need Help?

- **Client Guide**: see [FrontappClient Guide](client/guide.md) for Python-specific
  usage
- **Rate Limiting**: Front enforces per-endpoint limits; the client auto-retries 429s
  with exponential backoff
- **Pagination**: Front uses cursor-token pagination; the client's helpers walk
  `_pagination.next` tokens automatically

## OpenAPI Specification

The vendored spec is at [`frontapp-openapi.yaml`](frontapp-openapi.yaml).

It covers **139 paths across 233 operations** spanning every documented Front Core API
resource (conversations, messages, contacts, teammates, tags, inboxes, channels, rules,
signatures, templates, drafts, analytics, knowledge base, custom fields, accounts, and
more).

Upstream source:
[frontapp/front-api-specs](https://github.com/frontapp/front-api-specs).
