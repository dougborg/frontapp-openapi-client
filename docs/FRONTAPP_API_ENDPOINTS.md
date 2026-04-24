# Complete Frontapp API Endpoints Reference

This document provides a comprehensive list of all available Frontapp API endpoints that can be incorporated into the MCP Server.

**Last Updated**: 2025-10-21
**API Base URL**: `https://api2.frontapp.com`
**Documentation**: https://dev.frontapp.com/reference/introduction

---

## Current Implementation Status

The current MCP server ([frontapp_mcp.ts](frontapp_mcp.ts)) implements **23 tools** covering these areas:
- ✅ Conversations (list, get, search, update)
- ✅ Messages (list, get, send, reply)
- ✅ Contacts (list, get, create, update)
- ✅ Teammates (list, get)
- ✅ Tags (list, create)
- ✅ Inboxes (list, get)
- ✅ Comments (list, add)
- ⚠️ Analytics (basic get only)

**Coverage**: ~15-20% of total API surface area

---

## 1. Accounts (8 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/accounts` | List accounts | ❌ |
| POST | `/accounts` | Create account | ❌ |
| GET | `/accounts/{id}` | Get account | ❌ |
| PATCH | `/accounts/{id}` | Update account | ❌ |
| DELETE | `/accounts/{id}` | Delete account | ❌ |
| GET | `/accounts/{id}/contacts` | List account contacts | ❌ |
| POST | `/accounts/{id}/contacts` | Add contact to account | ❌ |
| DELETE | `/accounts/{id}/contacts` | Remove contact from account | ❌ |

**Use Cases**: Managing company/customer accounts, associating contacts with accounts

---

## 2. Analytics (4 endpoints) ⚠️ PARTIALLY IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/analytics/exports` | Create analytics export | ❌ |
| GET | `/analytics/exports/{id}` | Get analytics export | ❌ |
| POST | `/analytics/reports` | Create analytics report | ❌ |
| GET | `/analytics/reports/{id}` | Get analytics report | ❌ |
| GET | `/analytics` | Get analytics (basic) | ✅ |

**Use Cases**: Generate detailed reports on team performance, response times, message volumes

**Note**: Current implementation only has basic analytics endpoint. Need to add export/report creation and retrieval.

---

## 3. Attachments (4 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/comments/{comment_id}/attachments/{attachment_id}/download` | Download comment attachment | ❌ |
| GET | `/messages/{message_id}/attachments/{attachment_id}/download` | Download message attachment | ❌ |
| GET | `/message_templates/{template_id}/attachments/{attachment_id}/download` | Download template attachment | ❌ |
| GET | `/download/{attachment_id}` | Download attachment | ❌ |

**Use Cases**: Download files attached to messages, comments, or templates

**Important**: Downloading attachments counts against API rate limits

---

## 4. Channels (11 endpoints) ❌ NOT IMPLEMENTED

### Core Channel Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/channels` | List channels | ❌ |
| POST | `/channels` | Create channel | ❌ |
| GET | `/channels/{id}` | Get channel | ❌ |
| PATCH | `/channels/{id}` | Update channel | ❌ |
| POST | `/channels/{id}/validate` | Validate channel | ❌ |
| GET | `/teammates/{id}/channels` | List teammate channels | ❌ |
| GET | `/teams/{id}/channels` | List team channels | ❌ |

### Channel API (Message Sync)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/channels/{id}/inbound_messages` | Sync inbound message | ❌ |
| POST | `/channels/{id}/outbound_messages` | Sync outbound message | ❌ |
| PUT | `/channels/{id}/messages/{msg_id}/status` | Update external message status | ❌ |

### Application Message Templates

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| PUT | `/channels/{id}/application_message_templates` | Sync application message template | ❌ |

**Use Cases**: Manage communication channels (email, SMS, social media), sync messages with external systems

**Channel Types**: SMTP, IMAP, Twilio, Twitter, Facebook, Custom

---

## 5. Comments (6 endpoints) ⚠️ PARTIALLY IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/comments/{id}` | Get comment | ⚠️ (via conversation) |
| PATCH | `/comments/{id}` | Update comment | ❌ |
| GET | `/comments/{id}/mentions` | List comment mentions | ❌ |
| GET | `/conversations/{id}/comments` | List conversation comments | ✅ |
| POST | `/conversations/{id}/comments` | Add comment | ✅ |
| POST | `/comments/{id}/replies` | Add comment reply | ❌ |

**Use Cases**: Internal team discussions on conversations

**Note**: Comments are called "discussions" in the Front UI

---

## 6. Contacts (14 endpoints) ⚠️ PARTIALLY IMPLEMENTED

### Core Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/contacts` | List contacts | ✅ |
| POST | `/contacts` | Create contact | ✅ |
| GET | `/contacts/{id}` | Get contact | ✅ |
| PATCH | `/contacts/{id}` | Update contact | ✅ |
| DELETE | `/contacts/{id}` | Delete contact | ❌ |
| POST | `/contacts/merge` | Merge contacts | ❌ |

### Contact Relationships

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/contacts/{id}/conversations` | List contact conversations | ❌ |
| GET | `/contacts/{id}/notes` | List notes | ❌ |
| POST | `/contacts/{id}/notes` | Add note | ❌ |

### Contact Handles

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/contacts/{id}/handles` | Add contact handle | ❌ |
| DELETE | `/contacts/{id}/handles` | Delete contact handle | ❌ |

### Scope-Specific

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/teammates/{id}/contacts` | List teammate contacts | ❌ |
| POST | `/teammates/{id}/contacts` | Create teammate contact | ❌ |
| GET | `/teams/{id}/contacts` | List team contacts | ❌ |

**Use Cases**: Manage customer/contact information, track conversation history

**Special Feature**: Contacts support aliases like `alt:email:user@example.com`

---

## 7. Contact Groups (10 endpoints) ❌ DEPRECATED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/contact_groups` | List groups | ❌ Deprecated |
| POST | `/contact_groups` | Create group | ❌ Deprecated |
| DELETE | `/contact_groups/{id}` | Delete group | ❌ Deprecated |
| GET | `/contact_groups/{id}/contacts` | List contacts in group | ❌ Deprecated |
| POST | `/contact_groups/{id}/contacts` | Add contacts to group | ❌ Deprecated |
| DELETE | `/contact_groups/{id}/contacts` | Remove contacts from group | ❌ Deprecated |
| GET | `/teammates/{id}/contact_groups` | List teammate groups | ❌ Deprecated |
| POST | `/teammates/{id}/contact_groups` | Create teammate group | ❌ Deprecated |
| GET | `/teams/{id}/contact_groups` | List team groups | ❌ Deprecated |
| POST | `/teams/{id}/contact_groups` | Create team group | ❌ Deprecated |

**⚠️ DEPRECATED**: Use Contact Lists instead

---

## 8. Contact Lists (10 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/contact_lists` | List contact lists | ❌ |
| POST | `/contact_lists` | Create contact list | ❌ |
| DELETE | `/contact_lists/{id}` | Delete contact list | ❌ |
| GET | `/contact_lists/{id}/contacts` | List contacts in list | ❌ |
| POST | `/contact_lists/{id}/contacts` | Add contacts to list | ❌ |
| DELETE | `/contact_lists/{id}/contacts` | Remove contacts from list | ❌ |
| GET | `/teammates/{id}/contact_lists` | List teammate lists | ❌ |
| POST | `/teammates/{id}/contact_lists` | Create teammate list | ❌ |
| GET | `/teams/{id}/contact_lists` | List team lists | ❌ |
| POST | `/teams/{id}/contact_lists` | Create team list | ❌ |

**Use Cases**: Organize contacts into lists for segmentation and targeting

**Replaces**: Contact Groups (deprecated)

---

## 9. Conversations (19 endpoints) ⚠️ PARTIALLY IMPLEMENTED

### Core Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/conversations` | List conversations | ✅ |
| POST | `/conversations` | Create discussion conversation | ❌ |
| GET | `/conversations/search` | Search conversations | ✅ |
| GET | `/conversations/{id}` | Get conversation | ✅ |
| PATCH | `/conversations/{id}` | Update conversation | ✅ |
| PUT | `/conversations/{id}/assignee` | Update assignee | ❌ |

### Conversation Events & Followers

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/conversations/{id}/events` | List events | ❌ |
| GET | `/conversations/{id}/followers` | List followers | ❌ |
| POST | `/conversations/{id}/followers` | Add followers | ❌ |
| DELETE | `/conversations/{id}/followers` | Delete followers | ❌ |

### Conversation Relationships

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/conversations/{id}/inboxes` | List inboxes | ❌ |
| POST | `/conversations/{id}/links` | Add link | ❌ |
| DELETE | `/conversations/{id}/links` | Remove links | ❌ |

### Messages & Tags

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/conversations/{id}/messages` | List messages | ✅ |
| POST | `/conversations/{id}/messages` | Create message reply | ✅ (via reply) |
| PATCH | `/conversations/{id}/reminders` | Update reminders | ❌ |
| POST | `/conversations/{id}/tags` | Add tag | ❌ |
| DELETE | `/conversations/{id}/tags` | Remove tag | ❌ |

### Comments

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/conversations/{id}/comments` | List comments | ✅ |
| POST | `/conversations/{id}/comments` | Add comment | ✅ |

**Use Cases**: Full conversation lifecycle management, collaboration, tagging, linking

**Search Syntax**:
- `status:open` / `status:archived`
- `tag:urgent`
- `assignee:me` / `is:unassigned`
- `inbox:support`
- `after:2024-01-01` / `before:2024-12-31`
- Combine with `AND`, `OR`

---

## 10. Custom Fields (7 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/accounts/custom_fields` | List account custom fields | ❌ |
| GET | `/contacts/custom_fields` | List contact custom fields | ❌ |
| GET | `/conversations/custom_fields` | List conversation custom fields | ❌ |
| GET | `/custom_fields` | List all custom fields | ❌ |
| GET | `/inboxes/custom_fields` | List inbox custom fields | ❌ |
| GET | `/links/custom_fields` | List link custom fields | ❌ |
| GET | `/teammates/custom_fields` | List teammate custom fields | ❌ |

**Use Cases**: Retrieve custom field definitions and values

**Supported Types**: string, boolean, datetime, number, teammate, inbox, enum

**Note**: API only supports listing fields and updating values (no field creation via API)

---

## 11. Drafts (5 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/drafts` | Create draft | ❌ |
| GET | `/conversations/{id}/drafts` | List conversation drafts | ❌ |
| POST | `/channels/{id}/drafts` | Create draft reply | ❌ |
| DELETE | `/drafts/{id}` | Delete draft | ❌ |
| PATCH | `/drafts/{id}` | Edit draft | ❌ |

**Use Cases**: Manage draft messages before sending

**Important**: Editing/deleting drafts requires a `version` field to prevent conflicts (returns 409 if version mismatch)

---

## 12. Events (2 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/events` | List events | ❌ |
| GET | `/events/{id}` | Get event | ❌ |

**Use Cases**: Audit log, activity tracking, webhook alternative

**Search Parameters**:
- Event types (array)
- Date range (`before`, `after` timestamps)
- Inbox filtering

**Special Feature**: Event IDs are sequential and chronologically ordered (base 36 after `evt_` prefix)

---

## 13. Inboxes (10 endpoints) ⚠️ PARTIALLY IMPLEMENTED

### Core Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/inboxes` | List inboxes | ✅ |
| POST | `/inboxes` | Create inbox | ❌ |
| GET | `/inboxes/{id}` | Get inbox | ✅ |

### Inbox Relationships

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/inboxes/{id}/channels` | List inbox channels | ❌ |
| GET | `/inboxes/{id}/conversations` | List inbox conversations | ❌ |

### Access Control

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/inboxes/{id}/access` | List inbox access | ❌ |
| POST | `/inboxes/{id}/access` | Add inbox access | ❌ |
| DELETE | `/inboxes/{id}/access` | Remove inbox access | ❌ |

### Team Inboxes

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/teams/{id}/inboxes` | List team inboxes | ❌ |
| POST | `/teams/{id}/inboxes` | Create team inbox | ❌ |

**Use Cases**: Inbox management, access control, team organization

**Definition**: An inbox is a container of messages; channels post messages into inboxes

---

## 14. Knowledge Bases (14+ endpoints) ❌ NOT IMPLEMENTED

### Knowledge Base Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/knowledge_bases` | List knowledge bases | ❌ |
| POST | `/knowledge_bases` | Create knowledge base | ❌ |
| GET | `/knowledge_bases/{id}` | Get knowledge base | ❌ |
| GET | `/knowledge_bases/{id}/default` | Get KB with default locale | ❌ |
| PATCH | `/knowledge_bases/{id}/default` | Update KB in default locale | ❌ |
| PATCH | `/knowledge_bases/{id}/locales/{locale}` | Update KB in specific locale | ❌ |

### Category Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/knowledge_bases/{id}/categories` | List categories | ❌ |
| POST | `/knowledge_bases/{id}/categories` | Create category (default locale) | ❌ |
| GET | `/knowledge_base_categories/{id}` | Get category | ❌ |
| DELETE | `/knowledge_base_categories/{id}` | Delete category | ❌ |

### Article Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/knowledge_bases/{id}/articles` | List articles | ❌ |
| POST | `/knowledge_bases/{id}/articles` | Create article (default locale) | ❌ |
| GET | `/knowledge_base_articles/{id}` | Get article | ❌ |
| DELETE | `/knowledge_base_articles/{id}` | Delete article | ❌ |

**Use Cases**: Help center content management, multilingual knowledge bases

**Special Feature**: Full multilingual support with per-locale content

---

## 15. Links (5 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/links` | List links | ❌ |
| POST | `/links` | Create link | ❌ |
| GET | `/links/{id}` | Get link | ❌ |
| PATCH | `/links/{id}` | Update link | ❌ |
| GET | `/links/{id}/conversations` | List link conversations | ❌ |

**Use Cases**: Connect Front conversations with external systems (CRM, ticketing, project management)

**Definition**: Links associate Front conversations with external URLs and resources

---

## 16. Messages (7 endpoints) ⚠️ PARTIALLY IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/channels/{id}/incoming_messages` | Receive custom messages | ❌ |
| POST | `/channels/{id}/messages` | Create message | ✅ (via send_message) |
| POST | `/conversations/{id}/messages` | Create message reply | ✅ (via reply) |
| POST | `/channels/{id}/import` | Import message | ❌ |
| GET | `/messages/{id}` | Get message | ✅ |
| GET | `/messages/{id}/seen` | Get message seen status | ❌ |
| POST | `/messages/{id}/seen` | Mark message seen | ❌ |

**Use Cases**: Message management, read receipts, message import

**Message Types**: Email, SMS, WhatsApp, social media, custom channels

**Special Note**: Creating a message returns a `message_uid` (202 response), not the final `message_id`

**URL Pattern**: `https://app.frontapp.com/open/{message_id}` to open in Front UI

---

## 17. Message Templates & Folders (18 endpoints) ❌ NOT IMPLEMENTED

### Template Folder Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/message_template_folders` | List folders | ❌ |
| POST | `/message_template_folders` | Create folder | ❌ |
| GET | `/message_template_folders/{id}` | Get folder | ❌ |
| PATCH | `/message_template_folders/{id}` | Update folder | ❌ |
| DELETE | `/message_template_folders/{id}` | Delete folder | ❌ |
| GET | `/message_template_folders/{id}/children` | Get child folders | ❌ |
| POST | `/message_template_folders/{id}/children` | Create child folder | ❌ |
| GET | `/teammates/{id}/message_template_folders` | List teammate folders | ❌ |
| POST | `/teammates/{id}/message_template_folders` | Create teammate folder | ❌ |
| GET | `/teams/{id}/message_template_folders` | List team folders | ❌ |

### Message Template Operations

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/message_templates` | List templates | ❌ |
| POST | `/message_templates` | Create template | ❌ |
| GET | `/message_templates/{id}` | Get template | ❌ |
| PATCH | `/message_templates/{id}` | Update template | ❌ |
| DELETE | `/message_templates/{id}` | Delete template | ❌ |
| GET | `/message_templates/{id}/children` | Get child templates | ❌ |
| POST | `/message_templates/{id}/children` | Create child template | ❌ |

**Use Cases**: Canned responses, template management, team productivity

**Scope Levels**: Company, teammate, team

---

## 18. Rules (5 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/rules` | List all company rules | ❌ |
| GET | `/rules` | List rules | ❌ |
| GET | `/rules/{id}` | Get rule | ❌ |
| GET | `/teammates/{id}/rules` | List teammate rules | ❌ |
| GET | `/teams/{id}/rules` | List team rules | ❌ |

**Use Cases**: View automation rules, understand rule logic

**Definition**: Rules are conditions that trigger automatic actions

**Note**: API provides human-readable versions of rule conditions and actions

**Limitation**: API is read-only for rules (no creation/modification)

---

## 19. Shifts (10 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/shifts` | List shifts | ❌ |
| POST | `/shifts` | Create shift | ❌ |
| GET | `/shifts/{id}` | Get shift | ❌ |
| PATCH | `/shifts/{id}` | Update shift | ❌ |
| GET | `/shifts/{id}/teammates` | List shift teammates | ❌ |
| POST | `/shifts/{id}/teammates` | Add teammates to shift | ❌ |
| DELETE | `/shifts/{id}/teammates` | Remove teammates from shift | ❌ |
| GET | `/teammates/{id}/shifts` | List teammate shifts | ❌ |
| GET | `/teams/{id}/shifts` | List team shifts | ❌ |
| POST | `/teams/{id}/shifts` | Create team shift | ❌ |

**Use Cases**: Schedule management, availability tracking, timezone coverage

**Definition**: Shifts are recurring time intervals assigned to teammates; Front automatically manages availability status when shifts start/end

---

## 20. Signatures (8 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/signatures/{id}` | Get signature | ❌ |
| PATCH | `/signatures/{id}` | Update signature | ❌ |
| DELETE | `/signatures/{id}` | Delete signature | ❌ |
| GET | `/teammates/{id}/signatures` | List teammate signatures | ❌ |
| POST | `/teammates/{id}/signatures` | Create teammate signature | ❌ |
| GET | `/teams/{id}/signatures` | List team signatures | ❌ |
| POST | `/teams/{id}/signatures` | Create team signature | ❌ |

**Use Cases**: Email signature management at individual and team level

**Scope Levels**: Individual teammate, team

---

## 21. Tags (14 endpoints) ⚠️ PARTIALLY IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/tags` | List company tags | ✅ (via list_tags) |
| POST | `/tags` | Create company tag | ✅ (via create_tag) |
| GET | `/tags/{id}` | Get tag | ❌ |
| PATCH | `/tags/{id}` | Update tag | ❌ |
| DELETE | `/tags/{id}` | Delete tag | ❌ |
| GET | `/tags/{id}/children` | List tag children | ❌ |
| POST | `/tags/{id}/children` | Create child tag | ❌ |
| GET | `/tags/{id}/conversations` | List tagged conversations | ❌ |
| GET | `/teammates/{id}/tags` | List teammate tags | ❌ |
| POST | `/teammates/{id}/tags` | Create teammate tag | ❌ |
| GET | `/teams/{id}/tags` | List team tags | ❌ |
| POST | `/teams/{id}/tags` | Create team tag | ❌ |

**Use Cases**: Conversation categorization, organization, reporting

**Features**:
- Color highlighting
- Parent-child relationships (nested tags)
- Private vs shared tags

**Colors**: grey, pink, red, orange, yellow, green, light-blue, blue, purple

---

## 22. Teammates (5 endpoints) ⚠️ PARTIALLY IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/teammates` | List teammates | ✅ |
| GET | `/teammates/{id}` | Get teammate | ✅ |
| PATCH | `/teammates/{id}` | Update teammate | ❌ |
| GET | `/teammates/{id}/conversations` | List assigned conversations | ❌ |
| GET | `/teammates/{id}/inboxes` | List teammate inboxes | ❌ |

**Use Cases**: Team member management, assignment tracking

**Definition**: A teammate is a Front user, a member of your company

**Status Tracking**: `is_available` boolean indicates current availability

---

## 23. Teams / Workspaces (4 endpoints) ❌ NOT IMPLEMENTED

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/teams` | List teams | ❌ |
| GET | `/teams/{id}` | Get team | ❌ |
| POST | `/teams/{id}/teammates` | Add teammates to team | ❌ |
| DELETE | `/teams/{id}/teammates` | Remove teammates from team | ❌ |

**Use Cases**: Team/workspace organization, member management

**Note**: "Teams" in the API = "Workspaces" in the Front UI (API name is historical)

---

## Summary Statistics

| Category | Total Endpoints | Implemented | Percentage |
|----------|----------------|-------------|------------|
| **Accounts** | 8 | 0 | 0% |
| **Analytics** | 4 | 1 | 25% |
| **Attachments** | 4 | 0 | 0% |
| **Channels** | 11 | 0 | 0% |
| **Comments** | 6 | 2 | 33% |
| **Contacts** | 14 | 4 | 29% |
| **Contact Groups** | 10 | 0 | 0% (Deprecated) |
| **Contact Lists** | 10 | 0 | 0% |
| **Conversations** | 19 | 7 | 37% |
| **Custom Fields** | 7 | 0 | 0% |
| **Drafts** | 5 | 0 | 0% |
| **Events** | 2 | 0 | 0% |
| **Inboxes** | 10 | 2 | 20% |
| **Knowledge Bases** | 14 | 0 | 0% |
| **Links** | 5 | 0 | 0% |
| **Messages** | 7 | 3 | 43% |
| **Templates/Folders** | 18 | 0 | 0% |
| **Rules** | 5 | 0 | 0% |
| **Shifts** | 10 | 0 | 0% |
| **Signatures** | 8 | 0 | 0% |
| **Tags** | 14 | 2 | 14% |
| **Teammates** | 5 | 2 | 40% |
| **Teams** | 4 | 0 | 0% |
| **TOTAL** | **~200** | **23** | **~12%** |

---

## Priority Recommendations for Implementation

### High Priority (Common Use Cases)
1. **Drafts** - Essential for message composition workflow
2. **Events** - Critical for audit logs and activity tracking
3. **Tags (complete)** - Tag operations on conversations, hierarchical tags
4. **Conversation Operations (complete)** - Assignees, followers, links, reminders
5. **Contact Lists** - Modern replacement for deprecated Contact Groups
6. **Message Templates** - High-impact productivity feature

### Medium Priority (Power User Features)
1. **Channels** - Required for multi-channel management
2. **Teams/Workspaces** - Organization and permissions
3. **Accounts** - B2B/customer account management
4. **Links** - CRM and external system integration
5. **Custom Fields** - Extended data capture
6. **Analytics (complete)** - Full reporting capabilities

### Lower Priority (Specialized Features)
1. **Knowledge Bases** - Help center management
2. **Shifts** - Schedule/coverage management
3. **Signatures** - Email formatting
4. **Rules** - Read-only, for automation visibility
5. **Attachments** - Specialized download operations

### Skip
- **Contact Groups** - Deprecated, use Contact Lists instead

---

## Implementation Notes

### Authentication
- Bearer token via `Authorization: Bearer {token}` header
- Token from environment variable `FRONTAPP_API_TOKEN`
- Get tokens from Front Settings → Developers → API tokens

### Pagination
- Most list endpoints support `limit` (max 100, default 50) and `page_token`
- Use `pagination.next` from response for next page

### Rate Limiting
- Attachment downloads count against rate limits
- Standard rate limits apply to all endpoints

### Error Handling
- Axios errors include `error.response.data.message`
- Draft operations require `version` field (409 conflict if mismatch)
- Some operations return 202 Accepted with UIDs instead of final IDs

### Special Features
- **Contact Aliases**: `alt:email:user@example.com`, `alt:phone:+1234567890`
- **Event IDs**: Sequential, base-36 encoded (chronologically ordered)
- **Message URLs**: `https://app.frontapp.com/open/{message_id}`

---

## Next Steps

To expand the MCP server coverage:

1. **Phase 1** (High-value additions): Drafts, Events, Complete Tags, Contact Lists
2. **Phase 2** (Operational essentials): Channels, Teams, Complete Conversations
3. **Phase 3** (Extended capabilities): Accounts, Links, Custom Fields, Templates
4. **Phase 4** (Specialized features): Knowledge Bases, Shifts, Signatures, Analytics Reports

Each endpoint should follow the existing pattern:
- Add tool definition to `ListToolsRequestSchema`
- Add case to `CallToolRequestSchema` switch
- Implement private method for API call
- Handle errors consistently

---

## References

- **API Documentation**: https://dev.frontapp.com/reference/introduction
- **Base URL**: `https://api2.frontapp.com`
- **Authentication**: OAuth 2.0 or API Token
- **Current Implementation**: [frontapp_mcp.ts](frontapp_mcp.ts)
- **Project Documentation**: [CLAUDE.md](CLAUDE.md)
