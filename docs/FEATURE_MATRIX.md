# AVENIQ Feature-Matrix – Outlook-Parität & Nutzerwünsche

**Legende:** `I` = **implementiert und lokal getestet**, `P` = **teilweise** (stets Einschränkungen prüfen), `N` = **nicht implementiert** / Roadmap. Statusbezeichnungen beziehen sich auf **v0.1**, nicht auf ein abgeschlossenes Outlook-Äquivalent. `P0` = Kernfunktion, `P1` = wichtige Erweiterung, `P2` = Team/Pro, `P3` = Enterprise.
 **Umfang:** 183 einzelne Anforderungen; 35 implementiert, 22 teilweise, 126 offen.
Die vollständigen Journeys, Qualitätsziele, Userfeedback-Hypothesen und Sicherheitshinweise stehen in [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md), [`USER_FEEDBACK.md`](USER_FEEDBACK.md) und [`ROADMAP.md`](ROADMAP.md).

## Mail & Konten

| ID | Feature | Status v0.1 | Priorität |
|---|---|---|---|
| FD-001 | Lokale Anmeldung | **I** | P0 |
| FD-002 | Mehrere IMAP/SMTP-Konten definieren | **I** | P0 |
| FD-003 | IMAP INBOX Snapshot laden | **P** | P0 |
| FD-004 | IMAP Ordner lesen | **N** | P0 |
| FD-005 | IMAP Ordnerverwaltung | **N** | P1 |
| FD-006 | IMAP IDLE/Push | **N** | P0 |
| FD-007 | IMAP UIDVALIDITY/QRESYNC | **N** | P0 |
| FD-008 | Remote Gelesen/Markiert/Archiv spiegeln | **N** | P0 |
| FD-009 | Vereinter Posteingang | **P** | P0 |
| FD-010 | Konto-spezifische Filter | **N** | P0 |
| FD-011 | SMTP TLS Einzelversand | **I** | P0 |
| FD-012 | Entwurf erstellen/bearbeiten | **I** | P0 |
| FD-013 | Anlagen anhängen/senden | **N** | P0 |
| FD-014 | MIME Multipart sicher parsen | **P** | P0 |
| FD-015 | HTML sicher rendern | **N** | P0 |
| FD-016 | Externe Bilder blockieren | **I** | P0 |
| FD-017 | Zitierte E-Mail im Antwortentwurf | **P** | P1 |
| FD-018 | Antwort/Allen antworten/Weiterleiten | **N** | P0 |
| FD-019 | CC/BCC | **N** | P0 |
| FD-020 | Mehrere Signaturen | **N** | P1 |
| FD-021 | Konversations-Threading | **N** | P0 |
| FD-022 | Markieren / Stern (lokal) | **P** | P0 |
| FD-023 | Archivieren (lokal) | **P** | P0 |
| FD-024 | Tags/Kategorien | **N** | P1 |
| FD-025 | Anpinnen & Stummschalten | **N** | P1 |
| FD-026 | Snooze/Wiedervorlage | **N** | P1 |
| FD-027 | Senden planen | **N** | P1 |
| FD-028 | Undo Send mit verzögertem Versand | **N** | P0 |
| FD-029 | Templates und Schnellbausteine | **N** | P1 |
| FD-030 | Gesendet-Ansicht lokal | **P** | P0 |
| FD-031 | Spam/Junk und Quarantäne | **N** | P1 |
| FD-032 | Bounces und Zustellstatus | **N** | P1 |
| FD-033 | Read receipts / DSN | **N** | P2 |
| FD-034 | Kontodelegation & Shared Mailboxes | **N** | P2 |
| FD-035 | Outlook-Microsoft Graph Provider | **N** | P1 |
| FD-036 | Gmail OAuth Provider | **N** | P1 |
| FD-037 | JMAP Provider | **N** | P2 |
| FD-038 | EAS/EWS wo legitim | **N** | P3 |
| FD-039 | PGP E2EE und Schlüsselverwaltung | **N** | P2 |
| FD-040 | S/MIME signieren/verschlüsseln | **N** | P2 |
| FD-041 | EML Import/Export | **N** | P1 |
| FD-042 | MBOX Migration | **N** | P1 |
| FD-043 | PST Import mit geprüften Tools | **N** | P3 |
| FD-044 | Offline Mail-Datenbank | **N** | P1 |
| FD-045 | Lokale Suche FTS5 | **I** | P0 |
| FD-046 | Suche nach Absender/Datum/Konto | **P** | P1 |
| FD-047 | Saved Search / Suchordner | **N** | P1 |
| FD-048 | Regeln und Filter GUI | **N** | P1 |
| FD-049 | Sieve Export/Import | **N** | P2 |
| FD-050 | Tastatur-Shortcuts (Basis) | **P** | P1 |

## Kalender & Scheduling

| ID | Feature | Status v0.1 | Priorität |
|---|---|---|---|
| FD-051 | Lokale Monatsansicht | **I** | P0 |
| FD-052 | Lokale Termine anlegen | **I** | P0 |
| FD-053 | Lokale Termine bearbeiten/löschen | **I** | P0 |
| FD-054 | Mehrere lokale Kalender | **I** | P0 |
| FD-055 | Kalenderfarben | **I** | P1 |
| FD-056 | ICS Import/Export UTC/DATE | **P** | P0 |
| FD-057 | CalDAV Lesen (basic) | **P** | P0 |
| FD-058 | CalDAV bidirektional | **N** | P0 |
| FD-059 | Tagesansicht | **N** | P0 |
| FD-060 | 5-Tage-Ansicht | **N** | P1 |
| FD-061 | Wochenansicht | **N** | P0 |
| FD-062 | Jahresübersicht | **N** | P2 |
| FD-063 | Agenda / Timeline | **N** | P1 |
| FD-064 | Drag & Drop Events | **N** | P1 |
| FD-065 | Resize & Quick Create | **N** | P1 |
| FD-066 | Termine in mehreren Zeitzonen | **N** | P0 |
| FD-067 | TZID / VTIMEZONE RFC5545 | **N** | P0 |
| FD-068 | RRULE Wiederholungen | **P** | P0 |
| FD-069 | RDATE/EXDATE/Exceptions | **N** | P0 |
| FD-070 | RSVP und Meeting-Einladungen | **N** | P0 |
| FD-071 | iTIP iMIP Scheduling | **N** | P1 |
| FD-072 | Termine aus Mail erstellen | **N** | P1 |
| FD-073 | Teilnehmer / Gäste verwalten | **N** | P0 |
| FD-074 | Konflikterkennung | **N** | P0 |
| FD-075 | Frei/Gebucht Query | **N** | P1 |
| FD-076 | Meeting Slot Vorschläge | **N** | P1 |
| FD-077 | Arbeitszeiten/Feiertage | **N** | P1 |
| FD-078 | Ressourcen/Räume buchen | **N** | P2 |
| FD-079 | Shared Calendars ACL | **N** | P2 |
| FD-080 | Delegation Kalender | **N** | P2 |
| FD-081 | Kalender Push | **N** | P1 |
| FD-082 | Kalender Offline Sync | **N** | P1 |
| FD-083 | Erinnerungen/Benachrichtigungen | **N** | P0 |
| FD-084 | ICS Abo URLs | **N** | P2 |
| FD-085 | Google Calendar OAuth | **N** | P1 |
| FD-086 | Microsoft Graph Calendar | **N** | P1 |
| FD-087 | Meetinglinks (Teams/Meet/Jitsi) | **N** | P1 |
| FD-088 | Buchungslinks und Terminabstimmung | **N** | P2 |

## Kontakte / Personen

| ID | Feature | Status v0.1 | Priorität |
|---|---|---|---|
| FD-089 | Lokale Kontakte CRUD | **I** | P0 |
| FD-090 | Kontaktliste / Unternehmenszuordnung | **I** | P0 |
| FD-091 | CardDAV lesen | **N** | P1 |
| FD-092 | CardDAV bidirektional | **N** | P1 |
| FD-093 | Kontakte automatisch vorschlagen | **N** | P1 |
| FD-094 | Kontaktgruppen/Verteiler | **N** | P1 |
| FD-095 | Dubletten deduplizieren | **N** | P1 |
| FD-096 | vCard .vcf Import/Export | **N** | P1 |
| FD-097 | CSV Import/Export | **N** | P1 |
| FD-098 | Outlook/Gmail Kontakte Synchronisation | **N** | P2 |
| FD-099 | Kontakt-Avatare privat laden | **N** | P2 |
| FD-100 | Kontakt-Notizen und benutzerdef. Felder | **P** | P1 |
| FD-101 | Delegierte geteilte Adressbücher | **N** | P2 |
| FD-102 | CRM Sync mit VALDRIQ | **N** | P2 |

## Aufgaben / Notes

| ID | Feature | Status v0.1 | Priorität |
|---|---|---|---|
| FD-103 | Aufgaben CRUD | **I** | P0 |
| FD-104 | Aufgaben abhaken | **I** | P0 |
| FD-105 | Prioritäten | **I** | P0 |
| FD-106 | Fälligkeit | **I** | P0 |
| FD-107 | Aufgabe aus E-Mail | **P** | P1 |
| FD-108 | Unteraufgaben und Checklisten | **N** | P1 |
| FD-109 | Wiederkehrende Aufgaben | **N** | P1 |
| FD-110 | Erinnerungen | **N** | P0 |
| FD-111 | VTODO Sync | **N** | P1 |
| FD-112 | Aufgabenliste mit Kalender überlagern | **N** | P1 |
| FD-113 | Aufgaben delegieren | **N** | P2 |
| FD-114 | Notizen mit Markdown | **N** | P2 |
| FD-115 | Notizen mit Mail/Termin verlinken | **N** | P2 |
| FD-116 | Follow-up Pipelines | **N** | P2 |

## KI – ausschließlich Opt-in

| ID | Feature | Status v0.1 | Priorität |
|---|---|---|---|
| FD-117 | KI global AUS als Standard | **I** | P0 |
| FD-118 | Einzelzustimmung pro Anfrage | **I** | P0 |
| FD-119 | KI-Mail Zusammenfassung | **I** | P1 |
| FD-120 | KI-Antwortvorschlag | **I** | P1 |
| FD-121 | KI-Aufgabenvorschläge | **I** | P1 |
| FD-122 | Keine automatische KI-Weiterleitung | **I** | P0 |
| FD-123 | Keine KI-Autosendung | **I** | P0 |
| FD-124 | Lokales Modell statt Cloud | **N** | P1 |
| FD-125 | Provider-/Regionsauswahl | **N** | P1 |
| FD-126 | PII Redaktion vor Cloud-KI | **N** | P1 |
| FD-127 | KI-getriebene Triage/Filter mit Erklärung | **N** | P1 |
| FD-128 | KI-Terminevorschläge | **N** | P1 |
| FD-129 | KI Textsuche semantisch | **N** | P2 |
| FD-130 | Meeting Vorbereitung / Briefing | **N** | P2 |
| FD-131 | KI Kalenderkonflikt-Erklärung | **N** | P2 |
| FD-132 | Retrieval mit Quellenanzeige | **N** | P2 |
| FD-133 | KI Trainingsverbot/Provider-DPA Settings | **N** | P1 |
| FD-134 | KI Usage Audit pro Anfrage | **P** | P1 |
| FD-135 | Per-feature AI Permissions | **N** | P1 |

## UX / Offline / Barrierefreiheit

| ID | Feature | Status v0.1 | Priorität |
|---|---|---|---|
| FD-136 | Responsive Layout | **I** | P0 |
| FD-137 | Dark/Light | **I** | P0 |
| FD-138 | Lokalisierte deutsche UI | **I** | P0 |
| FD-139 | Progressive Web App Shell | **P** | P1 |
| FD-140 | Keine UI Telemetrie | **I** | P0 |
| FD-141 | Keine Remote Tracking Pixel | **I** | P0 |
| FD-142 | Kontextsensitive Menüs | **P** | P0 |
| FD-143 | Command Palette | **N** | P1 |
| FD-144 | Virtuelle Listen für 100k Mails | **N** | P0 |
| FD-145 | Shortcuts konfigurierbar | **N** | P1 |
| FD-146 | Nutzerdichte compact/comfortable | **N** | P1 |
| FD-147 | Reduced Motion | **N** | P1 |
| FD-148 | WCAG 2.2 AA | **P** | P0 |
| FD-149 | Screenreader-Audits | **N** | P0 |
| FD-150 | Offline Daten lesen | **N** | P1 |
| FD-151 | Offline Drafts und Mutation Queue | **N** | P1 |
| FD-152 | Konfliktcenter bei Sync | **N** | P0 |
| FD-153 | Status jeder Synchronisierung | **P** | P0 |
| FD-154 | Undo und Wiederherstellung | **N** | P1 |
| FD-155 | Globale Kontosuche | **P** | P0 |
| FD-156 | Multi-Device Config Sync | **N** | P2 |

## Enterprise & Security

| ID | Feature | Status v0.1 | Priorität |
|---|---|---|---|
| FD-157 | Scrypt Passwort-Hashing | **I** | P0 |
| FD-158 | HttpOnly Session Cookie | **I** | P0 |
| FD-159 | CSRF Schutz | **I** | P0 |
| FD-160 | Origin Prüfung | **I** | P0 |
| FD-161 | SMTP IMAP TLS Only | **I** | P0 |
| FD-162 | Secret ENV alias keine DB-Passwörter | **I** | P0 |
| FD-163 | Persistente Login Rate Limits | **P** | P0 |
| FD-164 | MFA / WebAuthn | **N** | P0 |
| FD-165 | OAuth2 PKCE und refresh rotation | **N** | P0 |
| FD-166 | RBAC / Mandantentrennung | **N** | P2 |
| FD-167 | Zero-trust API Tokens | **N** | P2 |
| FD-168 | Encrypted local data at rest | **N** | P0 |
| FD-169 | Verschlüsselte Backup/Restore | **N** | P0 |
| FD-170 | DSGVO Export/Löschkonzept | **P** | P1 |
| FD-171 | Audit Log unveränderlich | **N** | P2 |
| FD-172 | Provider OAuth scoped permissions | **N** | P1 |
| FD-173 | SPF/DKIM/DMARC Prüfung | **N** | P1 |
| FD-174 | DLP / Aufbewahrung / eDiscovery | **N** | P3 |
| FD-175 | SSO OIDC/SAML | **N** | P2 |
| FD-176 | SCIM User Provisioning | **N** | P3 |
| FD-177 | Secure Plugin Sandbox | **N** | P2 |
| FD-178 | Administrationsdashboard | **N** | P3 |
| FD-179 | Monitoring/OpenTelemetry optional | **N** | P2 |
| FD-180 | Backups automatisiert | **N** | P1 |
| FD-181 | DKIM ausgehend Provider | **N** | P2 |
| FD-182 | Resiliente Queue Workers | **N** | P0 |
| FD-183 | Migrations Versionsverwaltung | **N** | P1 |

## Definition of done

Ein Feature ist erst implementiert, wenn API + UI + Fehlerszenarien + automatisierter Test + Datenschutz-/Rechteeinordnung vorliegen. Ohne Provider-Livetest ist die Unterstützung des Providers stets eingeschränkt zu kennzeichnen. Ein visuelles Mockup ist kein Funktionsbeweis.

`I` bezieht sich auf lokale Implementierung und interne Tests (wo vorhanden), nicht auf vollständige E-Mail-/Kalenderprovider-Interoperabilität.
