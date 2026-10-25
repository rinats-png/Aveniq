# AVENIQ v0.1 API — developer preview

All endpoints are prefixed `/api` and served by the same origin as the web UI. All except `/health`, `/setup`, `/login`, `/session` require `aveniq_session` HttpOnly cookie; mutating requests also require `X-CSRF-Token`. The initial setup is only safe on loopback. This is a **local single-user API**, not a public integration contract.

## Auth

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Version and initialized state |
| POST | `/setup` | First admin only; `email`, `password` (>=12 chars) |
| POST | `/login` | Create session, return CSRF token |
| GET | `/session` | Check logged-in status and CSRF |
| POST | `/logout` | Invalidate current session |

## Mail

| Method | Route | Purpose |
|---|---|---|
| GET/POST | `/accounts` | List/create connection definitions (no secrets stored) |
| DELETE | `/accounts/{id}` | Delete definition and its cached messages |
| POST | `/accounts/{id}/sync` | Fetch recent IMAP INBOX UIDs, read-only |
| GET | `/messages?folder=inbox&account=&q=` | List local messages with optional FTS phrase query |
| GET | `/messages/{id}` | Read entire plaintext message body |
| PATCH | `/messages/{id}` | Set local unread/starred/archived booleans |
| POST | `/messages/demo` | Insert 4 fictional demo messages once |
| GET/POST | `/drafts` | List/create outgoing drafts |
| PATCH/DELETE | `/drafts/{id}` | Edit or delete a pending draft |
| POST | `/drafts/{id}/send` | Explicit send; body `{ "confirmation":"SEND_NOW" }` |

A successful SMTP call is recorded as `sent`, an uncertain/failed attempt is `uncertain` and blocks automated retry. Nothing is sent from the AI endpoint. **No attachment or HTML handling yet.**

## Calendar / people / tasks

| Method | Route | Purpose |
|---|---|---|
| GET/POST | `/calendars` | Local and read-only remote calendar definitions |
| POST | `/calendars/{id}/sync` | Import/refresh basic VEVENT from HTTPS CalDAV collection |
| GET/POST | `/events` | Event list / local create (timezone-aware ISO datetimes) |
| PATCH/DELETE | `/events/{id}` | Modify/delete local event only |
| GET/POST | `/ics` | Export basic .ics or import `{"ics":"...","calendar_id":1}` |
| GET/POST | `/contacts` | Contact list and create |
| PATCH/DELETE | `/contacts/{id}` | Contact edit/delete |
| GET/POST | `/tasks` | Task list/create |
| PATCH/DELETE | `/tasks/{id}` | Task edit/delete |

## Control and optional AI

| Method | Route | Purpose |
|---|---|---|
| GET/PATCH | `/settings` | Read/change `ai_enabled`; enabling requires `ack=I_EXPLICITLY_OPT_IN_TO_AI` |
| POST | `/ai` | `{"task":"summarize|draft_reply|extract_tasks", "text":"...", "consent":true}` plus globally enabled and configured API key |
| GET | `/audit` | Selected local activity history |
| GET | `/dashboard` | Current local counts and next calendar events |

## Examples (after login)

```bash
# Set CSRF and cookies from a separate login step (or use the UI).
curl -X POST http://127.0.0.1:8768/api/tasks \
  -H 'Content-Type: application/json' -H 'X-CSRF-Token: CSRF_FROM_LOGIN' \
  -H 'Cookie: aveniq_session=SESSION_FROM_LOGIN' \
  --data '{"title":"Projektplan fertigstellen","priority":1}'
```

For v1, use documented OpenAPI versioning, OAuth2 scopes, rate limiting, standardized errors, per-tenant row security and connector contracts. Do not expose this v0.1 API to untrusted networks.
