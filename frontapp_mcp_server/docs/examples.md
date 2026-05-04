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

## Drafting a reply to a customer (drafts-first, two-step confirm)

There is no direct-send tool — outbound replies always go through drafts. The agent
drafts; the human reviews the draft in Front's UI and clicks send.

```
User: "Let the customer on cnv_abc know we've shipped their replacement"

Model:
  # 1. Preview — confirm=False, no draft created.
  create_draft_reply(
    conversation_id="cnv_abc",
    body="Hi! We've shipped your replacement — tracking 1Z999AA10123456784.",
    channel_id="cha_xyz",
    confirm=False,
  )
  → {"preview": {"action": "create_draft_reply", "body_preview": "…"}, "confirmed": False}

  # 2. Create draft — only re-invoke with confirm=True after the user has agreed
  #    to the preview from step 1.
  create_draft_reply(
    conversation_id="cnv_abc",
    body="Hi! We've shipped your replacement — tracking 1Z999AA10123456784.",
    channel_id="cha_xyz",
    confirm=True,
  )
  → {"confirmed": True, "status_code": 202, "note": "Draft created. The human reviews in Front and clicks send."}
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

  # Apply — re-invoke with confirm=True after the user has agreed
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
2. **`confirm=True`** — executes the mutation. The agent must surface the preview from
   step 1 to the user and only re-invoke with `confirm=True` after the user has
   explicitly agreed.

This keeps the LLM from silently sending customer-facing messages, archiving active
conversations, or tagging things without a human in the loop. Spec-compliant MCP clients
should also be configured to prompt before destructive tool calls; the `destructiveHint`
annotation work is tracked separately.

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
