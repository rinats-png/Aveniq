# Engineering roadmap (not a claim of delivered features)

## Milestone 0 — Currently included local preview (v0.1)

- Single-user authentication, local SQLite and FTS5.
- Manual IMAP INBOX fetch/SMTP send, plaintext viewer, local mark/star/archive.
- Local contacts/tasks, month calendar, narrow UTC/Ganztag ICS and read-only CalDAV import.
- Optional OpenAI with global opt-in AND per-operation consent, no autonomous actions.
- Responsive browser/PWA shell, multi-account configuration, explicit fictional demo data.

**Gate:** Python and HTTP tests, JS syntax, no default cloud requests, no secret in Git.

## Milestone 1 — Real mail-client reliability

- OAuth2 PKCE integration for Gmail and Microsoft Graph, refresh token vault, provider capability discovery.
- UIDVALIDITY/QRESYNC delta loop, IMAP IDLE fallback polling, mailbox folders and flags mirrored both directions.
- MIME multipart + attachment metadata, sandboxed images and download, HTML sanitizer and remote-content opt-in.
- Durable drafts/outbox, cancellation window and scheduled send, send errors/unknown state recovery, Bcc/CC, signature management.
- Message threading by Message-ID/In-Reply-To/References, conversation grouping, mail folders, replies/forward/reply-all, auto-complete.
- Search filters and pagination, workload test with 100k messages; accessibility smoke tests.
- Rule engine with dry run and undo; spam/junk operations where provider supports.

**Gate:** Provider simulated integration suite + tested accounts for two independent IMAP providers. Zero duplicate delivery under faults. All UI controls backed by working APIs.

## Milestone 2 — Complete personal information management

- Adopt `ical.js` for RFC 5545 recurrence/time zone edge cases (including DST, EXDATE/RECURRENCE-ID).
- `tsdav` bidirectional CalDAV/CardDAV with sync tokens + ETag write preconditions, conflict UI.
- Meeting invitations (iTIP/iMIP), RSVP tracking, organizer vs attendee rules, cancellations and series changes.
- Day/week/month/agenda, drag resize, time-zone selector, reminders, holidays, color labels, free/busy and working hours.
- VTODO for tasks, imports .eml/.mbox/.ics/.vcf; migration tools for other clients.
- Transparent optional AI suggestions: scheduling, triage, drafting, summaries, task proposals, all with individual approvals.
- Browser state/data offline cache with encryption and consent, no auto sending without reconnection confirmation.

**Gate:** RFC/calendar fixture corpus, broken provider behavior suite, Android/browser/desktop accessibility tests.

## Milestone 3 — Team collaboration

- New authenticated multi-user backend, PostgreSQL, server-side encryption at rest, worker queue, per-tenant isolation and RBAC.
- Shared accounts/calendars, mail delegation and Send-As/On-Behalf permission checks, resource rooms and booking policies.
- Collaborator comments/tasks, safe template sharing, hosted meeting availability links, contact groups.
- Signed scoped plugin framework, client support capabilities, VALDRIQ connector with revocable consent.
- Automated backups, disaster recovery drill, audit trails, DLP/privacy and data retention controls.

**Gate:** tenant isolation penetration tests, disaster recovery rehearsal, OIDC/MFA/SSO feature tests.

## Milestone 4 — Enterprise / Outlook migration

- Microsoft Graph connector parity where available, Exchange permissions mapping, migration wizard from IMAP and permitted PST exports.
- Organization-admin console, IdP integration, mobile native wrappers where justified, optional E2EE with externally reviewed key management.
- Legal hold, retention and eDiscovery only after legal/security review; full admin provisioning/scim and compliance documentation.

**Gate:** formal third-party security review, documented interoperability matrix, documented privacy policy and a separate release sign-off.

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Gmail/M365 auth/permission changes | High | Official APIs, refresh token tests, provider test tenants |
| IMAP UID and destructive conflict bugs | Critical | UIDVALIDITY tracking, no silent destructive writes, fault-injection fixtures |
| Calendar timezone/recurrence mismatch | Critical | ICAL.js/RFC test fixtures, reject unknown semantics |
| SMTP duplicate send | Critical | Persistent state machine, manual reconciliation of unknown sends |
| Cross-tenant data leaks | Critical | Tenant-scoped access patterns, mandatory isolation tests |
| AI accidentally active / prompt injection | Critical | Fail-closed consent, allowlisted capabilities, test with hostile email text |
| GPL/AGPL license incompatibilities | High | No bundled code without legal review, SPDX inventory |
| User distrust due to misleading feature claims | High | Per-version matrix and executable acceptance criteria |
