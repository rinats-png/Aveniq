# Outlook-Nutzerkritik in überprüfbare Produktentscheidungen übersetzen

**Qualität der Evidenz:** Der vorherige Deep-Research-Bericht stützte viele Beschwerden auf Forenbeiträge, keine repräsentative Produktstudie. Einzelbeiträge illustrieren Probleme, belegen aber weder Häufigkeiten noch, dass sie jede Outlook-Variante betreffen. Besonders deutlich diskutiert: [Reddit r/Office365 – Very slow Outlook](https://www.reddit.com/r/Office365/comments/1chsuxb/very_slow_outlook/). Frühere Nutzer von Thunderbird heben eine einheitliche Inbox hervor: [Thunderbird](https://www.thunderbird.net/).

| Kritik / geäußerter Wunsch | Quelle / Evidenz | Maßnahme in AVENIQ | Erfolgskriterium |
|---|---|---|---|
| Outlook kann bei großen Postfächern träge sein | Einzelne Community-Berichte, kontextabhängig | Virtualisierte Listen, on-demand Fetch, lokaler FTS-Index, kontrollierbare Sync-Fenster | p95 erste Listenanzeige < 250 ms bei 100k synthetischen Mail-Metadaten; Hardware/Test klar dokumentieren |
| Suche liefert langsam oder unklare Resultate | Nutzerberichte inkl. Workarounds aus r/Office365 | Einheitliche Query-Sprache, lokaler Index, Such-Chips, Treffer-Hervorhebung | Reproduzierbare Such-Testmatrix mit Indexqualität und p95-Latenz |
| Ribbon und tief versteckte Aktionen erschweren Bedienung | UX-Hypothese aus Berichten | Kontextbezogene Aktion statt überladener globaler Toolbar; Tastaturbefehle | Usability-Test: Antwort, Archiv, Suche und Termin in <= 3 Interaktionen |
| Neues und klassisches Outlook verhalten sich unterschiedlich | Versionsbezogene Anwenderfeedbacks; offizielle Feature-Matrix erforderlich | Ein über alle Plattformen einheitliches Bedienmodell, Fähigkeiten pro Provider transparent | Gleiche Einstellung und Datenmodell in PWA/Desktop/Android |
| Multi-Account nicht klar / Posteingänge fragmentiert | Community-Wunsch und Thunderbird-Feature | Unified Inbox und Konto-Filtern, farbige Identität, Absenderkonto stets explizit | Kein Versand mit falscher Absenderidentität in Testläufen |
| Offline ist unklar und Sync meldet Konflikte schlecht | Produktanforderung aus Deep Research | Sync-Status, reproduzierbare Queue, Konfliktcenter und Offline-Indikator | Keine stillen Doppel-Sends, Status dokumentiert und nach Crash rekonstruierbar |
| Datenschutz und Telemetrie misstraut | Nutzerkommentare zu Unabhängigkeit | Keine Telemetrie, PWA nur shell cache, HTML remote images aus, Eigenhosting | Netzwerk-Audit: kein unnötiger 3rd-party call vor expliziter Aktion |
| KI-Empfehlungen werden als Black Box empfunden | UX-Anforderung, *keine* quantifizierte Umfrage | Globale KI-Voreinstellung AUS + pro Anfrage Einwilligung + „Warum?“ & „Was geht an Anbieter?“ | Getestet: 0 KI-Ausgangsrequests nach Installation/ohne Consent |
| Kalender und Inbox getrennt, Meeting-Nachverfolgung umständlich | Integrations-Anforderung | E-Mail → Termin / Task mit Preview und Freigabe | Einladungs-Parsing + RSVP-Testmatrix (geplant) |
| Gemeinsame Kalender/Delegation zu kompliziert | Gruppen-/Enterprise-Anforderung | Standardisierte ACLs, „Im Auftrag von“, explizite Berechtigungsanzeige | Kein Cross-Tenant-Leak bei Permission-Tests (geplant) |
| Viele überflüssige Funktionen | Nutzertyp-abhängige UX-Kritik | Basis-Modus „Mail & Kalender“; Expertenfunktionen über optionale Module | Weniger visuelle Dichte und messbare Task-Completion-Time |
| Anhänge, Bildvorschau, PDF, Outlook-PST-Import | Funktionales Paritätsziel | Isolierte Attachment-Services, Parser und Export/Import-Konverter | Malware-/Zipbomb-/MIME-Fuzz-Tests vor Produktion (geplant) |
| Relevanz-/Wichtig-Sortierung ist unverständlich | Hypothese nach Focused Inbox | Transparente Regeln, manuelles Training erst bei Zustimmung | Jede automatische Kategorie erklärt sich und ist rückgängig zu machen |
| Schnelle Aktionen / „Undo Send“ fehlen oder sind umständlich | Allgemeiner Nutzerwunsch, nicht in allen Outlook-Varianten identisch | Verzögerter Outbox-Commit mit abbrechbarem Countdown | Garantiert „Cancel“ vor SMTP Übergabe (geplant; v0.1 sendet sofort nach Bestätigung) |

**Priorisierung:** Datenschutz-Kontrolle, Mailzustellung, Sync-Zuverlässigkeit, Suche und Kalendergenauigkeit gehen vor KI-Effekten, Animation und Marketing-Versprechen.
