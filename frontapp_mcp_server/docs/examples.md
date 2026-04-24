# Frontapp MCP Server — Workflow Examples

Typical natural-language flows you can try with Claude Desktop once the server is
connected. Each example shows the underlying tool sequence.

> **Tip**: the `frontapp://help` resource surfaces the same information from inside the
> MCP client.

## Finding conversations to triage

```
User: "Show me the oldest open conversations that haven't been answered yet"

Model:
  list_conversations(q="status:open is:unassigned", limit=25)
  → [ConversationSummary(id="cnv_abc", subject="Order not received", …), …]
```

## Reading a conversation's history

```
User: "What's the latest on cnv_abc?"

Model:
  get_conversation(conversation_id="cnv_abc")
  → ConversationSummary(id=…, status="open", assignee_name="Jane Doe", …)

  list_conversation_messages(conversation_id="cnv_abc", limit=5)
  → [{body: "Hi, my order hasn't arrived…", author: {…}, created_at: …}, …]
```

## Searching with Front's query syntax

```
User: "What's still open from last week tagged 'shipping'?"

Model:
  search_conversations(
    query="status:open tag:shipping after:2026-04-17",
    limit=50,
  )
  → [ConversationSummary(…), …]
```

## Replying to a customer (two-step confirm)

```
User: "Let the customer on cnv_abc know we've shipped their replacement"

Model:
  # 1. Preview — confirm=False, no send.
  reply_to_conversation(
    conversation_id="cnv_abc",
    body="Hi! We've shipped your replacement — tracking 1Z999AA10123456784.",
    confirm=False,
  )
  → {"preview": {"action": "reply_to_conversation", "body_preview": "…"}, "confirmed": False}

  # 2. Send — confirm=True triggers ctx.elicit to ask the user to approve.
  reply_to_conversation(
    conversation_id="cnv_abc",
    body="Hi! We've shipped your replacement — tracking 1Z999AA10123456784.",
    confirm=True,
  )
  → {"confirmed": True, "status_code": 202, "note": "…message enqueued."}
```

## Reassigning and re-tagging

```
User: "Move cnv_abc to the billing team and tag it 'refund-requested'"

Model:
  # Preview
  update_conversation(
    conversation_id="cnv_abc",
    assignee_id="tea_billing_triage",
    tag_ids=["tag_refund_requested"],
    confirm=False,
  )
  → {"preview": {...}, "confirmed": False}

  # Apply — elicits approval
  update_conversation(..., confirm=True)
  → {"confirmed": True, "status_code": 200}
```

## Internal notes (teammates only)

```
User: "Leave an internal note on cnv_abc reminding us to check stock on SKU-1234"

Model:
  # Internal comments never reach the customer. Still two-step confirm.
  add_conversation_comment(
    conversation_id="cnv_abc",
    body="Reminder: confirm SKU-1234 is actually in stock before promising a ship date.",
    confirm=True,
  )
  → {"confirmed": True, "status_code": 201}
```

## Archiving a resolved conversation

```
User: "Archive cnv_abc now that we've sorted it out"

Model:
  update_conversation(
    conversation_id="cnv_abc",
    status="archived",
    confirm=True,
  )
  → {"confirmed": True, "status_code": 200}
```

## Why two-step confirm?

Every tool that changes data takes a `confirm: bool = False` parameter:

1. **`confirm=False`** — returns a `preview` dict showing exactly what would be sent. No
   side effects, no rate-limit cost beyond the tool call itself.
2. **`confirm=True`** — elicits explicit user approval via the MCP host's `ctx.elicit`
   flow (e.g. a Claude Desktop dialog), _then_ executes.

This keeps the LLM from silently sending customer-facing messages, archiving active
conversations, or tagging things without a human in the loop.

## Front search syntax cheat sheet

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

Combine with `AND` / `OR`: `status:open AND tag:urgent`.
