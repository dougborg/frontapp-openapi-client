# Cookbook: Common Patterns (TypeScript)

Ready-to-use recipes for the Frontapp TypeScript client. See the [guide](guide.md) for
the conceptual overview.

## Contents

- [List conversations with a filter](#list-conversations-with-a-filter)
- [Full-text search with Front syntax](#full-text-search-with-front-syntax)
- [Get one conversation with messages](#get-one-conversation-with-messages)
- [Send a reply](#send-a-reply)
- [Archive + retag in one call](#archive--retag-in-one-call)
- [Add an internal comment](#add-an-internal-comment)
- [Walking cursor pagination manually](#walking-cursor-pagination-manually)
- [List workspace reference data](#list-workspace-reference-data)
- [Testing patterns](#testing-patterns)

## List conversations with a filter

```typescript
import { FrontappClient } from "frontapp-client";

const client = await FrontappClient.create();

const { data } = await client.listConversations({
  query: { q: "status:open tag:urgent", limit: 25 },
});

for (const conv of data?._results ?? []) {
  console.log(`${conv.id}: ${conv.subject ?? "(no subject)"} — ${conv.status}`);
}
```

## Full-text search with Front syntax

```typescript
const { data } = await client.searchConversations({
  path: { query: "status:open AND tag:urgent AND after:2026-04-01" },
  query: { limit: 50 },
});

console.log(`${data?._results?.length ?? 0} matches`);
```

Full query syntax:

| Query               | Description                 |
| ------------------- | --------------------------- |
| `status:open`       | Open conversations          |
| `status:archived`   | Archived                    |
| `tag:urgent`        | Tagged urgent               |
| `assignee:me`       | Assigned to the token owner |
| `is:unassigned`     | Unassigned                  |
| `inbox:support`     | In a named inbox            |
| `after:2024-01-01`  | Updated after a date        |
| `before:2024-12-31` | Updated before a date       |

Combine with `AND` / `OR`.

## Get one conversation with messages

```typescript
// Conversation itself
const { data: conv } = await client.getConversationById({
  path: { conversation_id: "cnv_abc" },
});

// Messages inside it
const { data: msgs } = await client.listConversationMessages({
  path: { conversation_id: "cnv_abc" },
  query: { limit: 10 },
});

for (const m of msgs?._results ?? []) {
  console.log(
    `[${new Date(m.created_at * 1000).toISOString()}] ${m.body?.slice(0, 80)}`,
  );
}
```

## Send a reply

```typescript
const response = await client.replyToConversation({
  path: { conversation_id: "cnv_abc" },
  body: {
    body: "Thanks for reaching out — we're tracking it down now.",
    author_id: "tea_xyz", // optional; defaults to token owner
  },
});

// Front returns 202 Accepted; message is enqueued for delivery.
console.log(response.response.status); // → 202
```

## Archive + retag in one call

```typescript
await client.updateConversation({
  path: { conversation_id: "cnv_abc" },
  body: {
    status: "archived",
    tag_ids: ["tag_resolved", "tag_fulfilled"],
  },
});
```

## Add an internal comment

```typescript
// Teammate-only — never reaches the customer.
await client.addComment({
  path: { conversation_id: "cnv_abc" },
  body: {
    body: "FYI: shipped from the secondary warehouse.",
    author_id: "tea_xyz",
  },
});
```

## Walking cursor pagination manually

Auto-pagination is on by default, but if you want explicit control:

```typescript
let cursor: string | undefined = undefined;
const all: ConversationResponse[] = [];

while (true) {
  const { data } = await client.listConversations({
    query: { q: "status:open", limit: 100, page_token: cursor },
  });
  all.push(...(data?._results ?? []));
  const next = data?._pagination?.next;
  if (!next) break;
  cursor = new URL(next).searchParams.get("page_token") ?? undefined;
  if (!cursor) break;
}

console.log(`Collected ${all.length} open conversations`);
```

## List workspace reference data

```typescript
const [tags, inboxes, teammates] = await Promise.all([
  client.listTags(),
  client.listInboxes(),
  client.listTeammates(),
]);

console.log(`tags: ${tags.data?._results?.length ?? 0}`);
console.log(`inboxes: ${inboxes.data?._results?.length ?? 0}`);
console.log(`teammates: ${teammates.data?._results?.length ?? 0}`);
```

Useful for turning readable names into ids before mutations (e.g. mapping `"Support"` to
an inbox id for `updateConversation`).

## Testing patterns

Mock the generated SDK methods directly with `vi.fn()`:

```typescript
import { describe, it, expect, vi } from "vitest";
import type { ConversationResponse } from "frontapp-client/types";

describe("my business logic", () => {
  it("tags urgent open conversations", async () => {
    const client = {
      listConversations: vi.fn().mockResolvedValue({
        data: {
          _results: [{ id: "cnv_a", status: "open", tags: [] } as ConversationResponse],
        },
      }),
      updateConversation: vi.fn().mockResolvedValue({
        response: new Response(null, { status: 200 }),
      }),
    };

    await myBusinessLogic(client as any);

    expect(client.updateConversation).toHaveBeenCalledWith({
      path: { conversation_id: "cnv_a" },
      body: expect.objectContaining({
        tag_ids: expect.arrayContaining(["tag_urgent"]),
      }),
    });
  });
});
```

Or use MSW (`msw`) to intercept at the fetch layer if you want end-to-end tests without
hitting Front.
