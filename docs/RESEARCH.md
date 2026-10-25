# Deep-Research-Auswertung · Open Source statt Outlook

**Stand:** 25. Oktober 2026. Diese Datei ist eine technische Auswertung der im Chat durchgeführten Deep Research plus nachträglicher Verifikation einzelner Repositories. Sie ersetzt keine aktuelle Vollprüfung sämtlicher Anbieter-/Produktversionen.

## Entscheidungsgrundlage

Outlook ist nicht eine einzige Anwendung: „klassisches Outlook für Windows“, „neues Outlook für Windows“, Outlook im Web und Mobile unterscheiden sich bei Offline-Funktionen, Add-ins, Kontotypen, Delegation, Importformaten und Sicherheit. Die Desktop- und Web-Erfahrungen dürfen in einer Produktmatrix nicht vermischt werden. Eine echte Alternative muss zunächst die *standardisierten* Funktionen für Privatnutzer und kleine Teams zuverlässig beherrschen, bevor sie vollständige Microsoft-365-/Exchange-Enterprise-Funktionen verspricht.

Die Deep Research identifizierte u. a. Thunderbird, Roundcube, RainLoop, Mailpile, Radicale, sabre/dav, Citadel, Kolab, Nextcloud und CalDAV/IMAP-Bibliotheken. Nach zusätzlicher Prüfung würden wir **RainLoop nicht als neue Produktbasis** verwenden: SnappyMail ist ein deutlich modernerer Fork, aber seinerseits AGPL; Mailpile ist eher als Designreferenz geeignet als als Core-Dependency. [SnappyMail](https://github.com/the-djmaze/snappymail), [Mailpile](https://github.com/mailpile/Mailpile).

## Outlook-Bausteine, nach denen das Produkt modelliert wird

| Ebene | Gegenstand | Typische technische Konsequenz |
|---|---|---|
| E-Mail | Konten, Ordner, IMAP/Exchange, Threads, Anhänge, Senden, Regeln, Labels, Kategorien | MIME-Parser, IMAP/SMTP, später Graph/JMAP, persistente Synchronisation |
| Kalender | Tag/Woche/Monat, Wiederholung, Teilnehmer, freigegeben, Frei/Gebucht, Ressourcen, Zeitzonen | RFC 5545 / CalDAV / iTIP / Scheduling-Protokolle |
| Kontakte | Personen, Organisationen, Verteiler, AutoComplete, Freigabe | CardDAV / vCard / Kontaktidentitäten |
| Aufgaben | Flagged messages, Prioritäten, wiederkehrende Aufgaben, Erinnerungen | Lokale To-dos, VTODO und Synchronisation |
| Produktivität | Quick Steps, Regeln, Suchordner, Kategorien, Snooze, Undo-send, Vorlagen | Regelengine, Outbox, Suchindex, kontrollierte Automatisierung |
| Collaboration | Exchange Shared Mailboxes, Delegation, Raum- und Ressourcenbuchung, Teams | Scope-/Berechtigungsmodell, Microsoft Graph Connector |
| Enterprise | MDM, Auditing, Retention, DLP, eDiscovery, Datenresidenz, SSO | **Separate** kostenintensive Governance-Schicht |

## Warum wir keinen monolithischen Fork bauen

- **Roundcube**: ausgereifte IMAP-Webmail-Funktionen, aber PHP-Monolith und GPL-Lizenz; eigener Kalender müsste umfangreich integriert werden. [Repository](https://github.com/roundcube/roundcubemail).
- **SnappyMail**: modernerer RainLoop-Fork, aber AGPL 3.0 und nicht das gesamte Zielsystem. [Repository](https://github.com/the-djmaze/snappymail).
- **Thunderbird**: starke Mail-/Kalender-Implementierung, Mozilla Public License 2.0; Desktop-Architektur und Erweiterungssystem, kein geeigneter Startpunkt für eine unabhängige browserbasierte SaaS-/PWA-Oberfläche. [Projekt](https://www.thunderbird.net/).
- **Nextcloud/Kolab**: als Groupware-Alternativen stark, aber erheblicher Betriebs- und Lizenz-/Fork-Aufwand und anderer Produktfokus.
- **Radicale**: sehr guter *separater* CalDAV-/CardDAV-Server, nicht ohne Weiteres als Webclient-Bibliothek einbinden. [Repository](https://github.com/Kozea/Radicale).
- **sabre/dav**: gutes Framework, BSD-Lizenz, aber PHP-Baustein, kein kompletter Client. [Repository](https://github.com/sabre-io/dav).

**Empfehlung:** Neue, klar lizenzierte Anwendung mit Protokoll-Adapter-Schicht und optionalen **extern** betriebenen Groupware-Diensten. Kein „blindes Mergen“ von Copy-left- und kommerziell lizenzierten Projekten in einen MIT-Codebestand.

## Forschungsgrenzen

Die vorangegangene Deep Research fasste nicht jede Outlook-Funktionsvariante auf Release-Ebene zusammen, unterschied einzelne Nutzerberichte nicht immer sauber nach Version und enthielt teils unpräzise Aktivitätsbehauptungen (etwa zu RainLoop). Das folgende Feature-Register ist deshalb ein **technischer Zielkatalog und Entwurf**, keine gemessene Marktverteilung von Nutzerwünschen und kein Nachweis gleichwertiger Microsoft-Lizenzfunktionalität.

Wichtige Nutzerrückmeldungen und deren Evidenz befinden sich separat in [`USER_FEEDBACK.md`](USER_FEEDBACK.md). Vor einem Produktlaunch: mehrsprachige qualitative Interviews, instrumentierte Nutzertests und offizielle Outlook-Version-Mapping-Tests durchführen.
