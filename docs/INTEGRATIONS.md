# Integrationshandbuch

## IMAP/SMTP

- Only secure IMAPS 993 and SMTP TLS 465 / STARTTLS 587.
- ENV aliases (the UI stores only the alias): `AVENIQ_ACCOUNT_WORK_USER`, `AVENIQ_ACCOUNT_WORK_PASSWORD`. Choose a distinct uppercase prefix per account.
- This connector supports standard app-password/password auth only. Modern Gmail and Microsoft 365 enterprise tenants can require OAuth2: **not implemented**. Disable IMAP password login at the provider when not required.
- The importer gets recent 150 INBOX UIDs; no IMAP IDLE, UIDVALIDITY/CONDSTORE delta tracking, sync of other folders, remote flag changes or attachment handling yet. Local labels/stars/archive do **not** update IMAP state. Deleted remote messages are not removed locally.
- SMTP confirmation is explicit. If delivery outcome is unknown, do not resubmit automatically. Look in the provider Sent folder first.

## CalDAV

- Provide the direct collection URL over HTTPS, not a generic login page, under the Calendar creation dialog.
- Configure `AVENIQ_CAL_TEAM_USER` and `AVENIQ_CAL_TEAM_PASSWORD` on the server.
- Implementation uses `PROPFIND Depth:1` to enumerate `.ics` files, GET each changed ETag, and imports basic VEVENTs.
- Limitations: read-only; no sync-token, scheduling/RSVP, time-zone VTIMEZONE rules, RDATE/EXDATE exceptions, CardDAV or remote ACL support. For robust syncing add `tsdav` and `ical.js` in the planned TypeScript worker.
- Because the URL is user-configured, deploy with strict network egress/SSRF rules and trusted calendars only.

## iCalendar

- Export and import basic VEVENT data via `GET /api/ics` and `POST /api/ics`.
- UTC timestamps and DATE all-day events are supported. TZID events are **rejected**, not quietly shifted. Do not use the v0.1 importer for mission-critical complex recurring calendars.

## AI

- `AVENIQ_OPENAI_API_KEY` and `AVENIQ_OPENAI_MODEL` on the server.
- **Both** global settings opt-in **and** per single message checkbox are required; no background scans.
- API call uses OpenAI Responses API, no SDK or vendor model client shipped. Users must understand privacy and data processing. No body is sent when either consent gate is false.
- Action output is a non-binding suggestion, not stored automatically; human approval required for any send/calendar mutation. Future integrations can add **local AI** as an explicit alternative, but never quietly fall back to cloud.

## Microsoft Graph / Exchange / Gmail / JMAP

Not yet supported. Planned adapters must use official provider APIs and OAuth2 PKCE with least scopes, rotating encrypted refresh tokens, tenant consent/permission constraints, bounded background syncing, and provider-specific integration tests. EWS/ActiveSync and PST/OST interoperability must not be promised without validating licensed implementations and version behavior.

## VALDRIQ interoperability (planned)

VALDRIQ: <https://github.com/rinats-png/VALDRIQ->. Use an OAuth-like narrow consented integration with minimal data (`message_id`, `contact_id`, `thread_id`, `meeting_id`, `follow_up_due_at`) rather than copying entire mailbox contents into the CRM. Only inbound, existing-customer or otherwise legally permitted marketing workflows; never bypass explicit contact eligibility in VALDRIQ or auto-send messages without approval. Add tests for revoked consent, data deletion, access control and idempotent updates.
