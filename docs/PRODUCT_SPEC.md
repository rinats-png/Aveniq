# AVENIQ — Product Requirements Document (PRD)

**Target:** A trustworthy Outlook-class communication workspace, starting with a coherent self-hosted personal edition and evolving toward a multi-user professional suite. This document is the **complete target scope**, not a declaration of code parity.

## Product principles

1. **A quiet interface:** contextual actions, calm colors, no crowded ribbon, readable at 100% zoom and accessible keyboard flows.
2. **Mail and time belong together:** messages, people, tasks and meetings share references; the underlying ownership and permissions remain separate.
3. **Do not lose or duplicate data:** offline mutations require journaling, idempotency keys, conflict reconciliation and export paths.
4. **Standards first:** IMAP4rev2/SMTP/JMAP, CalDAV/CardDAV, iCalendar/iTIP/iMIP, MIME and RFC-compatible search. Exchange/M365 providers via separate official API adapters.
5. **Fast and transparent search:** speed budgets, user-visible index state, filters, correct ranking and origin-traceable results.
6. **AI not assumed:** off by default, capability-scoped opt-in, exact data disclosure before every cloud call, human preview for any side effect. Support optional on-device/local provider when implemented.
7. **Provider honesty:** distinguish native, limited, unsupported and not-yet-implemented features per provider/account.
8. **Portable by design:** export messages as .eml/.mbox, calendars as .ics, contacts as .vcf, tasks as iCalendar VTODO / JSON, configuration safely; do not silently destroy server data.

## Personas and use cases

| Persona | Jobs-to-be-done | Priority |
|---|---|---|
| Individual | Manage 2–6 accounts, fast inbox, appointments, reminders, contacts | P0 |
| Freelancer / small company | Shared calendar, meeting links, several identities, customer follow-ups | P1 |
| Executive / assistant | Delegation, shared mailboxes, meeting scheduling and conflict management | P2 |
| IT Administrator | SSO, MFA, retention, compliance, migration, admin observability | P3 |
| Privacy-conscious user | Self-host, encryption, no tracking, opt-in features | P0 |

## Essential product journeys

### 1. Account onboarding

User chooses personal or work, selects provider, is told **exactly** what permissions are needed. Native OAuth2 PKCE where required. App tests incoming/outgoing/calendar/contacts permissions independently. User is shown capabilities and limitations, import estimated volume, storage requirement, sync mode and security posture. Only ask follow-ups when needed, do not ask for a value already provided. On error, show actionable diagnosis without exposing tokens.

### 2. Reading and replying

Unified inbox loads cached metadata quickly. Open a message in a reading pane with stripped active content, inspect attachments in sandbox. Support conversation threads, snooze, assign categories, move folder, flag, pin, mute, create task, create calendar event, share link with authorized users, reply/forward. Expose exactly which edits are **local** vs already written to provider. Reply composer supports proper identities, attachments, rich text *and* plain text, accessibility, draft autosave, scheduled send, undo-send window, trustworthy delivery state.

### 3. Calendar scheduling

Create meetings on any authorized calendar, compute free/busy including delegated and resource calendars, honor working hours/time zones, suggest valid slots without claiming certainty, invite participants via CalDAV scheduling/iTIP or Exchange Graph. Correctly handle recurrence, daylight-saving transitions, all-day events, RSVP, exceptions, cancellations and meeting series edits. Never silently shift dates. Exports preserve UIDs and TZIDs.

### 4. Tasks and follow-ups

Transform message into a task with retained message reference. Assign due date, priority, tags, subtasks, reminders, repeat schedules. Link tasks to contacts and optionally existing CRM records. Every automatic task proposed by an AI requires explicit accept/save action. Cross-sync with CalDAV VTODO or provider APIs must show conflicts.

### 5. Privacy and AI

At first start all AI capabilities false. Toggle reveals provider, model, exact processing region (where known), logging/retention controls, on-device vs remote tradeoffs and data categories. Per action, ask consent again, show *selected text only*, allow redaction and audit what was transmitted. No model should gain broad inbox access or permission to send, reply, RSVP, forward or delete. Never treat email body instructions as privileged instructions; implement prompt-injection defense-in-depth and tests.

## Visual system

- Scandinavian modern, ink navy, desaturated teal, soft boundaries, generous typography, practical density controls.
- Screens: **Today**, **Inbox**, **Calendar**, **Contacts**, **Tasks**, **Notes**, **Search**, **Rules**, **Accounts**, **Integrations**, **AI settings**. Each screen offers a compact/full mode and is functional, not decorative.
- Mail: three-pane layout on desktop, adaptive single-column navigation on mobile; split reading pane or separate window; consistent context actions.
- Calendar: day, 5-day, week, month, year, timeline/agenda, shared availability overlay; keyboard navigation; color & accessibility palettes.
- Keyboard: Ctrl/Cmd+K global search, compose shortcuts, J/K navigation, E archive, S star (configurable), Ctrl+Enter confirm send; strong visual focus.
- Dark/light modes, density settings, reduced motion, responsive touch sizes. Internationalization from a message catalogue rather than string literals for public beta.

## Quality objectives (measurable, not promises of v0.1)

| KPI | Target for production beta | How to measure |
|---|---|---|
| Initial interactive inbox | p95 <= 1.5 s for cached first paint | Mid-range laptop, standard network, 50k cached messages |
| Local search | p95 <= 250 ms for indexed queries | 100k synthetic messages with realistic lengths |
| Data-loss tolerance | 0 silent lost drafts | Crash + power-off test matrix |
| Duplicate send | 0 from automatic retries after ambiguous provider acceptance | Fault injection SMTP and outbox tests |
| Calendar correctness | 100% on RFC regression suite | DST, TZID, recurrence and invitation fixtures |
| Unauthorized AI requests | 0 when global toggle OFF or per-use consent missing | Network spy integration tests |
| Screen reader usability | WCAG 2.2 AA target | Keyboard, NVDA, VoiceOver and axe test suites |
| Sync observability | Every failed sync has human-readable status | Synthetic offline/online/conflict tests |
| Interoperability | Tested providers and unsupported features listed | Provider matrix automated smoke tests |

## What not to promise prematurely

- “Full Exchange parity”, “E2EE” (without audited cryptography/key management), “Instant offline delivery”, “CalDAV scheduling” from a read-only adapter, “AI never processes your data” when explicitly opted into remote AI, “all clients” when only one is tested, or any compliance certification not obtained.
- Cloud mailbox provider support without the actual OAuth2 permissions, policies and provider tests.
- Commercial resale rights over third-party GPL/AGPL/Proprietary modules merely by referencing their repository.

## Product release definition

A `v1.0` can be called “Outlook alternative for individuals and small teams” after safe full mail sync and OAuth2, complete MIME/attachments, editable bidirectional CalDAV/CardDAV, recurrence+invites, offline draft/outbox, robust search, multi-user permission boundaries, security and privacy review, backups/migration and cross-platform accessibility pass. **Enterprise parity** is a different and larger milestone.
