# FrontappClient Guide (TypeScript)

The **FrontappClient** is the TypeScript client for Front's
[Core API](https://dev.frontapp.com/reference/introduction). It wraps the generated
`@hey-api/openapi-ts` SDK with a resilient fetch layer: automatic retries, 429-aware
backoff, and cursor-token pagination helpers.

The Core API is large — 233 operations across conversations, messages, contacts,
teammates, tags, inboxes, channels, rules, analytics, and more. Every operation is
available as a typed method on the client.

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

const client = await FrontappClient.create(); // reads FRONTAPP_API_KEY

// List recent open conversations tagged urgent
const { data } = await client.listConversations({
  query: { q: "status:open tag:urgent", limit: 25 },
});

for (const conv of data._results ?? []) {
  console.log(`${conv.id}: ${conv.subject ?? "(no subject)"} — ${conv.status}`);
}
```

Get an API token at **Front → Settings → Developers → API tokens**.

## Authentication

Resolved in this order:

1. `apiKey` option on `FrontappClient.create()`
2. `FRONTAPP_API_KEY` environment variable
3. Node `.env` file (loaded by your app, not by this library — see below)

```typescript
const client = FrontappClient.withApiKey("your-api-token");
```

### Loading `.env` files

**Node 20.6+**:

```bash
node --env-file=.env your-script.js
```

**Node 18–20.5**: add `dotenv` to your project:

```typescript
import "dotenv/config";
import { FrontappClient } from "frontapp-client";

const client = FrontappClient.withApiKey(process.env.FRONTAPP_API_KEY!);
```

## Configuration

```typescript
const client = await FrontappClient.create({
  apiKey: "your-api-token",
  baseUrl: "https://api2.frontapp.com", // default shown

  retry: {
    maxRetries: 5,
    backoffFactor: 1.0, // 1s, 2s, 4s, 8s, 16s
    respectRetryAfter: true,
  },

  pagination: {
    maxPages: 100,
    maxItems: undefined, // cap total items when set
    defaultPageSize: 50, // Front default; max 100
  },

  autoPagination: true, // disable globally when false
});
```

## Retry Behavior

| Status                | GET / PUT / DELETE | POST / PATCH |
| --------------------- | ------------------ | ------------ |
| 429 Too Many Requests | Retry              | Retry        |
| 502 / 503 / 504       | Retry              | No retry     |
| Other 4xx             | No retry           | No retry     |
| Network error         | Retry              | Retry        |

POST/PATCH are retried on 429 because rate-limit responses mean the request **was not
processed** — retrying is safe even for non-idempotent methods.

## Pagination

Front uses cursor-based pagination. List responses include `_pagination.next` as a full
URL; pass `page_token` back to the same endpoint to fetch the next page:

```typescript
let cursor: string | null | undefined = null;
const all: ConversationResponse[] = [];

while (true) {
  const { data } = await client.listConversations({
    query: { q: "status:open", limit: 100, page_token: cursor ?? undefined },
  });
  all.push(...(data._results ?? []));
  const next = data._pagination?.next;
  if (!next) break;
  cursor = new URL(next).searchParams.get("page_token");
}
```

Auto-pagination (walking the cursor chain for you) is enabled by default — the transport
middleware detects list endpoints and collects across pages up to `pagination.maxPages`
/ `pagination.maxItems`.

### Disabling auto-pagination

```typescript
// Per-request — pass an explicit page_token
const page2 = await client.listConversations({
  query: { page_token: "ce787da…" },
});

// Globally
const client = await FrontappClient.create({ autoPagination: false });
```

## Error Handling

```typescript
import {
  parseError,
  AuthenticationError,
  RateLimitError,
  ValidationError,
  ServerError,
} from "frontapp-client";

const response = await client.replyToConversation({
  path: { conversation_id: "cnv_abc" },
  body: { body: "Hi there." },
});

if (response.error) {
  const error = parseError(response);

  if (error instanceof AuthenticationError) {
    console.error("Invalid API token");
  } else if (error instanceof RateLimitError) {
    console.error(`Rate limited — retry after ${error.retryAfter ?? "?"}s`);
  } else if (error instanceof ValidationError) {
    console.error("Validation failed:", error.details);
  } else if (error instanceof ServerError) {
    console.error(`Server error ${error.statusCode}`);
  } else {
    console.error(`Error ${error.statusCode}: ${error.message}`);
  }
}
```

## Using the Generated SDK

`@hey-api/openapi-ts` generates a typed SDK method for every operation (233 total).
They're available as properties on the client, or as importable functions:

```typescript
import {
  FrontappClient,
  listConversations,
  getConversationById,
  updateConversation,
  replyToConversation,
} from "frontapp-client";

const client = await FrontappClient.create();

// Via client methods
const { data } = await client.listConversations({
  query: { q: "status:open", limit: 50 },
});

// Or via standalone functions (pass the sdk)
const { data: conv } = await getConversationById({
  client: client.sdk,
  path: { conversation_id: "cnv_abc" },
});
```

## Common operations cheat sheet

```typescript
// Conversations (helper vertical live today)
await client.listConversations({ query: { q: "status:open", limit: 25 } });
await client.getConversationById({ path: { conversation_id: "cnv_abc" } });
await client.updateConversation({
  path: { conversation_id: "cnv_abc" },
  body: { status: "archived" },
});
await client.replyToConversation({
  path: { conversation_id: "cnv_abc" },
  body: { body: "Hi!", author_id: "tea_xyz" },
});
await client.addComment({
  path: { conversation_id: "cnv_abc" },
  body: { body: "Internal note.", author_id: "tea_xyz" },
});

// Contacts, tags, inboxes, teammates
await client.listContacts();
await client.listTags();
await client.listInboxes();
await client.listTeammates();
```

Browse `src/generated/sdk.gen.ts` for the full 233-method surface.

## Environment Variables

- `FRONTAPP_API_KEY` — Front API token for bearer auth.
- `FRONTAPP_BASE_URL` — override the base URL (optional).

## Troubleshooting

### "No API key configured"

Set `FRONTAPP_API_KEY` or pass `apiKey` to `FrontappClient.create()`.

### Persistent 429s

Front enforces per-endpoint rate limits. The client retries automatically; if you see
persistent rate limits, slow down or batch reads into larger `limit=100` pages.

### Auto-pagination fetching too much

Cap it with `pagination.maxPages`, `pagination.maxItems`, or explicitly pass a
`page_token` to get a single specific page.
