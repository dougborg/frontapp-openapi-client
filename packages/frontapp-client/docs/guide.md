# FrontappClient Guide (TypeScript)

The **FrontappClient** is the TypeScript client for the
[Frontapp API](https://api2.frontapp.com). It wraps the generated
`@hey-api/openapi-ts` SDK with a resilient fetch layer: automatic retries, 429-aware
backoff, and auto-pagination across list endpoints.

Frontapp is a small API (seven endpoints covering order status lookup and update), so
this client is intentionally compact.

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
const response = await client.get("/orders");
const { data, meta } = await response.json();

console.log(`Found ${meta.total} orders (page ${meta.current_page}/${meta.last_page})`);
for (const order of data) {
  console.log(`${order.name}: ${order.status?.name ?? "(no status)"}`);
}
```

## Authentication

Resolved in this order:

1. `apiKey` option on `FrontappClient.create()`
1. `FRONTAPP_API_KEY` environment variable
1. Node `.env` file (loaded by your app, not by this library — see below)

```typescript
const client = FrontappClient.withApiKey("sk_live_...");
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
  apiKey: "sk_live_...",
  baseUrl: "https://api2.frontapp.com", // default shown

  retry: {
    maxRetries: 5,
    backoffFactor: 1.0, // 1s, 2s, 4s, 8s, 16s
    respectRetryAfter: true,
  },

  pagination: {
    maxPages: 100,
    maxItems: undefined, // cap total items when set
    defaultPageSize: 100, // Frontapp's max per_page
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

POST/PATCH are retried on 429 because rate limiting is transient. `/comment` and
`/bulk-status` have a 5/min limit; plan your workload accordingly.

## Auto-Pagination

On by default for GET requests without an explicit `page` parameter. The client walks
`{data, meta}` envelopes using `meta.last_page` as the stop condition and concatenates
all pages into a single response.

```typescript
// Auto-paginated — collects every page
const response = await client.get("/orders", { status_code: "st000002" });
const { data, pagination } = await response.json();
console.log(
  `${pagination.total_items} orders across ${pagination.collected_pages} pages`,
);
```

### Disabling

```typescript
// Per-request: explicit page disables auto-pagination
const response = await client.get("/orders", { page: 2, per_page: 50 });

// Globally:
const client = await FrontappClient.create({ autoPagination: false });
```

### Raw-array responses

`GET /statuses` and `GET /orders/{id}/viable-statuses` return plain JSON arrays, not
`{data, meta}` envelopes. The client detects this and passes them through untouched — no
pagination attempted.

## Error Handling

```typescript
import {
  parseError,
  AuthenticationError,
  RateLimitError,
  ValidationError,
  ServerError,
} from "frontapp-client";

const response = await client.post("/orders/123/status", {
  status_code: "st000003",
});

if (!response.ok) {
  const body = await response.json();
  const error = parseError(response, body);

  if (error instanceof AuthenticationError) {
    console.error("Invalid API key");
  } else if (error instanceof RateLimitError) {
    console.error(`Rate limited — retry after ${error.retryAfter ?? "?"}s`);
  } else if (error instanceof ValidationError) {
    // Frontapp ValidationErrorResponse: { message, errors: { field: [messages] } }
    for (const [field, messages] of Object.entries(error.details)) {
      console.error(`${field}: ${messages.join("; ")}`);
    }
  } else if (error instanceof ServerError) {
    console.error(`Server error ${error.statusCode}`);
  } else {
    console.error(`Error ${error.statusCode}: ${error.message}`);
  }
}
```

## Using the Generated SDK

`@hey-api/openapi-ts` generates typed SDK functions for each endpoint. Use them with the
resilient client for full type safety:

```typescript
import {
  FrontappClient,
  listOrders,
  getOrder,
  updateOrderStatus,
} from "frontapp-client";

const client = await FrontappClient.create();

const { data, error } = await listOrders({
  client: client.sdk,
  query: { status_code: "st000002", per_page: 50 },
});

if (data) {
  console.log(`Got ${data.data.length} orders`);
}
```

Available SDK functions mirror the nine endpoints:

- `listOrders`
- `getOrder`
- `lookupOrder`
- `updateOrderStatus`
- `addOrderComment`
- `setOrderDueDate`
- `bulkUpdateOrderStatus`
- `getStatuses`
- `getViableStatuses`

## HTTP Method Shortcuts

```typescript
// GET — auto-paginated for /orders by default
const orders = await client.get("/orders");
const order = await client.get("/orders/6110375248088");
const statuses = await client.get("/statuses"); // raw array, not paginated

// POST — all Frontapp mutations are POSTs
const result = await client.post("/orders/6110375248088/status", {
  status_code: "st000003",
  comment: "Shipped via UPS.",
  public: true,
  email_customer: true,
});
```

Frontapp does not expose `PUT`, `PATCH`, or `DELETE`.

## Environment Variables

- `FRONTAPP_API_KEY` — bearer token for authentication
- `FRONTAPP_BASE_URL` — override the base URL (optional)

## Troubleshooting

### "No API key configured"

Set `FRONTAPP_API_KEY` or pass `apiKey` to `FrontappClient.create()`.

### Persistent 429s

The `/comment` and `/bulk-status` endpoints have a 5/min rate limit. The client retries
automatically; if you see persistent rate limits, slow down.

### Auto-pagination fetching too much

Cap it with `pagination.maxPages`, `pagination.maxItems`, or explicitly pass
`{ page: 1 }` to get a single page.
