# SECURITY.md — local developer preview, not public SaaS

## Current controls
- Local-only HTTP bind; loopback-only published port via Docker Compose.
- First administrator setup; scrypt password hash with random salt; session cookie HttpOnly/SameSite=Strict; server-side SHA-256 session token hash; CSRF on writes; same-origin restriction; selected audit entries.
- No external tracker, analytics script, auto-fetch of remote images or embedded email HTML. Message bodies shown as escaped plaintext.
- Mail and CalDAV credentials are **not persisted**: a database account stores a server ENV prefix such as `AVENIQ_ACCOUNT_WORK`. Credentials must be provided in the host/container environment.
- SMTP requires a deliberate send action and exact confirmation. Unknown delivery outcome uses `uncertain` and blocks silent retry.
- KI/AI requires both global opt-in and explicit per-request checkbox, and API credentials. No automatic sending.

## Not implemented / exposure warnings
- No MFA, SSO, per-user accounts, role-based authorization, lockout persistence, encrypted SQLite storage, data retention scheduler, security audit-grade logs, server-side sync worker queues, traffic rate limiting or external monitoring.
- Not suitable for open internet without an HTTPS reverse proxy, a local/private initial setup, origin whitelist, credential vault, user isolation and a security audit. Frontend build/deployment access and authentication layers require special attention.
- CalDAV includes user-supplied HTTPS URLs: use only trusted endpoints. Host-level firewall/egress controls must prevent access to internal metadata services; SSRF hardening and IP/DNS resolution revalidation needed before multi-user hosting.
- Secrets in environment variables can be accessed by privileged host/container users; an encrypted token vault + key rotation is required for public deployments.
- Database backups may contain personal or confidential email; encrypt backups and enforce retention/erasure. Data exported to third parties (including any optional AI) requires applicable legal basis and provider review.
- Current calendar parser intentionally rejects TZID local time; modern iTIP/iCalendar implementations require a real RFC5545 library and comprehensive tests.
- FTS5 search index contains plaintext message bodies. Disk-level encryption should be enabled and encrypted per-account stores built before organizational deployment.

## Local usage rules
1. Run v0.1 on a trusted machine over 127.0.0.1; do first-time setup before anything is reachable from networks.
2. Use a strong unique passphrase; use provider-specific app passwords rather than main account passwords if supported.
3. Do not commit `.env`, databases, exports or backups.
4. Run the tests, audit dependencies and inspect the privacy settings before adding provider accounts.
5. Do not use this for unsolicited campaign sends; comply with applicable advertising and privacy law.

## Reporting vulnerabilities
Privately report sensitive issues to the repository owner. Do not disclose real user messages, tokens, keys or password material in public GitHub Issues.
