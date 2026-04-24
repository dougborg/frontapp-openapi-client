# frontapp-client

TypeScript/JavaScript client for the
[Front Core API](https://dev.frontapp.com/reference/introduction) with automatic
resilience. Generated from Front's official OpenAPI spec via
[hey-api](https://heyapi.dev) and wrapped with a transport layer that adds retry,
rate-limit awareness, and cursor-token pagination helpers.

## Features

- **Generated SDK** — full typed method per operation (233 total) via
  `@hey-api/openapi-ts` + `@hey-api/client-fetch`.
- **Automatic retries** — exponential backoff with configurable retry limits; idempotent
  methods retried on 5xx, all methods retried on 429.
- **Rate-limit awareness** — respects 429 + `Retry-After` with exponential backoff
  fallback.
- **Cursor pagination helpers** — walks `_pagination.next` tokens for paginated list
  endpoints.
- **Type safety** — full TypeScript types generated from the OpenAPI spec.
- **Browser & Node.js** — works in both environments.
- **Tree-shakeable** — only import what you need.

## Installation

```bash
npm install frontapp-client
# or
pnpm add frontapp-client
# or
yarn add frontapp-client
```

## Quick Start

```typescript
import { FrontappClient } from "frontapp-client";

// Token from FRONTAPP_API_KEY env var (or .env)
const client = await FrontappClient.create();

// Or provide the token directly
const client = FrontappClient.withApiKey("your-api-token");

// List open conversations tagged urgent
const { data } = await client.listConversations({
  query: { q: "status:open tag:urgent", limit: 25 },
});
console.log(`${data._results.length} results`);
```

## Types-only import

```typescript
import type {
  ConversationResponse,
  MessageResponse,
  ContactResponse,
} from "frontapp-client/types";

function render(conv: ConversationResponse) {
  // ...
}
```

## Configuration

```typescript
const client = await FrontappClient.create({
  apiKey: "your-api-token", // or FRONTAPP_API_KEY env var

  baseUrl: "https://api2.frontapp.com", // default shown

  retry: {
    maxRetries: 5,
    backoffFactor: 1.0, // 1s, 2s, 4s, 8s, 16s
    respectRetryAfter: true,
  },

  pagination: {
    maxPages: 100,
    maxItems: undefined, // cap total items when set
    defaultPageSize: 50, // Front's default; max 100
  },

  autoPagination: true, // disable per-request with an explicit `page_token`
});
```

## Retry Behavior

Mirrors the Python client — including the deliberate choice to retry POST/PATCH on 429
(rate-limit 429s mean the request wasn't processed, so retrying is safe even for
non-idempotent methods):

| Status Code      | GET/PUT/DELETE | POST/PATCH |
| ---------------- | -------------- | ---------- |
| 429 (Rate limit) | Retry          | Retry      |
| 502, 503, 504    | Retry          | No retry   |
| Other 4xx        | No retry       | No retry   |
| Network error    | Retry          | Retry      |

## Pagination

Front uses cursor-based pagination. List responses include `_pagination.next` as a full
URL; pass the `page_token` query parameter back to the list endpoint to fetch the next
page.

Auto-pagination walks the cursor chain for you:

```typescript
const { data } = await client.listConversations({
  query: { q: "status:open" },
});
// data._results contains collected items across pages
// Capped by pagination.maxPages / pagination.maxItems in config.
```

To disable for one call, pass an explicit `page_token`:

```typescript
const page2 = await client.listConversations({
  query: { page_token: "ce787da…" },
});
```

## Error Handling

```typescript
import {
  FrontappClient,
  parseError,
  AuthenticationError,
  RateLimitError,
  ValidationError,
} from "frontapp-client";

const response = await client.reply({
  conversationId: "cnv_abc",
  body: { body: "Hi there." },
});

if (response.error) {
  const error = parseError(response);

  if (error instanceof AuthenticationError) {
    console.error("Invalid API token");
  } else if (error instanceof RateLimitError) {
    console.error(`Rate limited. Retry after ${error.retryAfter}s`);
  } else if (error instanceof ValidationError) {
    console.error("Validation errors:", error.details);
  } else {
    console.error(`Error ${error.statusCode}: ${error.message}`);
  }
}
```

Available error classes:

- `AuthenticationError` (401)
- `RateLimitError` (429) — includes `retryAfter` seconds when present
- `ValidationError` (422)
- `ServerError` (5xx)
- `NetworkError` — connection failures
- `FrontappError` — base class

## Generated SDK methods

Every Front Core API operation is available as a named method on the client. Common
ones:

```typescript
// Conversations
await client.listConversations({ query: { q: "status:open" } });
await client.getConversationById({ path: { conversation_id: "cnv_abc" } });
await client.updateConversation({
  path: { conversation_id: "cnv_abc" },
  body: { status: "archived" },
});
await client.replyToConversation({
  path: { conversation_id: "cnv_abc" },
  body: { body: "Thanks!", author_id: "tea_xyz" },
});

// Contacts
await client.listContacts();
await client.getContact({ path: { contact_id: "crd_abc" } });

// Tags, Inboxes, Teammates
await client.listTags();
await client.listInboxes();
await client.listTeammates();
```

Every method returns `{ data, error, response }` — `data` is present on 2xx, `error` on
4xx/5xx. See `src/generated/sdk.gen.ts` for the full surface.

## Environment Variables

- `FRONTAPP_API_KEY` — Front API token for bearer auth.
- `FRONTAPP_BASE_URL` — override the base URL (optional).

### Loading from `.env` files

**Node.js 20.6+** (recommended):

```bash
node --env-file=.env your-script.js
```

**Node.js 18–20.5** — use `dotenv`:

```bash
npm install dotenv
```

```typescript
import "dotenv/config";
import { FrontappClient } from "frontapp-client";

const client = FrontappClient.withApiKey(process.env.FRONTAPP_API_KEY!);
```

> This library supports Node.js 18+ but does not bundle `dotenv`. If you need `.env`
> loading on Node 18–20.5, install `dotenv` in your project.

## Documentation

- **[Client Guide](docs/guide.md)** — comprehensive usage guide
- **[Cookbook](docs/cookbook.md)** — common patterns and recipes
- **[Testing Guide](docs/testing.md)** — testing strategy
- **[Architecture Decisions](docs/adr/README.md)** — design rationale

## License

MIT
