# AVENIQ — Codex / engineering instructions

## Mission
Build a user-controlled, fast Outlook alternative with Mail, Calendar, Contacts, Tasks, Search, Rules, and optional opt-in AI. Use the finished deep-research feature register in `docs/FEATURE_MATRIX.md` and product specification in `docs/PRODUCT_SPEC.md`. NEVER mistake a requirement or mock for completed functionality.

## Initial assessment before modifying code
1. Run the tests and check `git status` / the current branch; do not overwrite user changes.
2. Read `README.md`, `SECURITY.md`, `docs/ARCHITECTURE.md`, `docs/FEATURE_MATRIX.md`, and `docs/USER_FEEDBACK.md`.
3. Identify the exact currently supported API and likely missing integrations.
4. State which requirements are implemented, partial, planned, and blocked. Include explicit acceptance tests and security implications.
5. Select one vertical feature slice at a time. Prefer completely working end-to-end behavior over numerous cosmetic controls.
6. Work without waiting for unnecessary clarifications. Ask the operator only for prerequisites required for external accounts (provider, OAuth client, credentials, policy), and NEVER print/store secret values in source or logs.

## Non-negotiable requirements
- AI opt-in **off** by default. A real global opt-in and per-action explicit consent are required. Secrets from the environment do not imply consent. No background scanning or sending to a model. When disabled, no AI requests, training or telemetry.
- Never permit AI to send email, RSVP, schedule or delete without a separate human approval for that action.
- Remote message HTML, images, and attachments are untrusted: sanitize, sandbox and block remote loads. No HTML injection through DOM APIs.
- Account passwords and OAuth tokens must remain server-side in an encrypted credential vault for any public deployment; environment-only credential references in v0.1.
- All incoming SMTP/IMAP/DAV/ICS/MIME data are untrusted, validate sizes and formats, normalize time zones and report unsupported semantics instead of silently corrupting calendars.
- Use idempotent sync (UIDVALIDITY, UID, modseq where supported), durable outbox state, retry correctness, and traceable conflicts before declaring true offline-first or complete IMAP synchronization.
- Preserve user data and privacy in every migration. Use schema migrations and encrypted backup/restore tests before general availability.
- Respect third-party source licenses. Track dependency versions and SPDX licenses, especially GPL/AGPL and commercial-only modules.
- Add tests for backend API, permission boundaries, emails, calendar recurrence, synchronisation conflicts, response sanitization, accessibility and offline workflows.

## Release gate
A feature is `implemented` only after verified end-to-end tests; `partial` if just local/client/read-only; `planned` if only specified. Check documented functionality against the current implementation. Don't advertise complete Outlook parity until the full matrix meets defined acceptance criteria.

## Suggested next concrete sprint
Implement OAuth2 PKCE+token rotation and Gmail/M365 connectors with explicit consent, IMAP UIDVALIDITY-aware sync, IMAP read/star/archive writeback, MIME attachment metadata and safe attachment download. Add fake IMAP/SMTP server test fixtures and fix up sync progress/error presentation. Then start robust calendar recurrence (ICAL.js), CalDAV sync tokens + ETags, iTIP invitations and RSVP. The phase plan is in `docs/ROADMAP.md`.
