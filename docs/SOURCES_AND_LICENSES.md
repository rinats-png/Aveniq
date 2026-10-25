# Open-source Bausteine und Lizenzstrategie

Checked conceptually on 25 October 2026. **Verify exact versions, SPDX metadata, current security advisories and commercial obligations before importing any dependency.** No third-party source has been copied into this repository.

| Component | Repository | Typical license | Proposed role | Status |
|---|---|---|---|---|
| Thunderbird | <https://github.com/mozilla/releases-comm-central> (official primary source is Mozilla Mercurial) | MPL-2.0 | functional reference / desktop-first alternative | Not bundled |
| Roundcube | <https://github.com/roundcube/roundcubemail> | GPL-3.0 / plugin exceptions | webmail reference or independent deployment | Not bundled |
| SnappyMail | <https://github.com/the-djmaze/snappymail> | AGPL-3.0 | modern webmail reference, potential standalone server | Not bundled |
| RainLoop | <https://github.com/RainLoop/rainloop-webmail> | check exact branch | Legacy reference only; prefer maintenance review of SnappyMail | Not bundled |
| Mailpile | <https://github.com/mailpile/Mailpile> | AGPL-3.0 in reviewed research | historical privacy/search inspiration, archived | Not bundled |
| Radicale | <https://github.com/Kozea/Radicale> | GPL-3.0 | standalone CalDAV/CardDAV server | Not bundled |
| sabre/dav | <https://github.com/sabre-io/dav> | BSD-3-Clause | DAV protocol server framework | Not bundled |
| Nextcloud Mail | <https://github.com/nextcloud/mail> | check repo license | groupware alternative; not embedding | Not bundled |
| Nextcloud Calendar | <https://github.com/nextcloud/calendar> | check repo license | calendar UX and scheduling reference | Not bundled |
| ImapFlow | <https://github.com/postalsys/imapflow> | MIT | production-grade IMAP backend / IDLE | Planned, not installed |
| PostalMime | <https://github.com/postalsys/postal-mime> | MIT-0 | MIME safe parsing | Planned, not installed |
| Nodemailer | <https://github.com/nodemailer/nodemailer> | MIT-0 in recent versions | SMTP MIME / attachments | Planned, not installed |
| tsdav | <https://github.com/natelindev/tsdav> | MIT | CalDAV/CardDAV adapters | Planned, not installed |
| ICAL.js | <https://github.com/kewisch/ical.js> | MPL-2.0 | RFC5545 recurrence/time zones | Planned, not installed |
| FullCalendar Standard | <https://github.com/fullcalendar/fullcalendar> | MIT | complex time/day/week/month grid | Planned, not installed |
| FullCalendar Premium | <https://fullcalendar.io/license> | Commercial/conditional | resource scheduling | **NOT** bundled; separate license required |

**License trap:** MIT code may *integrate over a network* with services under other licenses without necessarily copying their code; embedding/copyleft obligations depend on distribution/deployment and exact licensing. AGPL/GPL source must not be represented as MIT. MPL file-level obligations must be honored for modifications. Consult legal advice before commercial redistribution.

## Source validation updates from the post-research check

- `imapflow`: current releases and MIT on npm, [ImapFlow](https://www.npmjs.com/package/imapflow).
- `mailparser`: maintainers explicitly call it *maintenance mode* and recommend PostalMime for new projects, [mailparser README](https://github.com/nodemailer/mailparser).
- `tsdav`: current TypeScript WebDAV/CalDAV/CardDAV client, [tsdav](https://github.com/natelindev/tsdav).
- `ical.js`: RFC5545 and vCard parsing, MPL-2.0, [ICAL.js](https://github.com/kewisch/ical.js).
- FullCalendar Standard is MIT, Premium requires additional rights, [licensing](https://fullcalendar.io/license).
