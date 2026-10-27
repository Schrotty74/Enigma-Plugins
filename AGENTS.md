# Enigma-Plugins: Repository-Regeln

- Jedes Plugin liegt vollständig unter `plugins/<Plugin>/`. Der zugehörige Arbeitskontext liegt unter `context/<Plugin>/`.
- Vor Änderungen die vollständigen betroffenen Dateien und `context/<Plugin>/AGENTS.md`, `PROJECT_CONTEXT.md`, `NEXT_STEPS.md` und `CHAT_TEMPLATE.md` lesen. Vor neuen Funktionen zuerst prüfen, was schon vorhanden ist.
- Den Kontext nach wesentlichen Änderungen und am Aufgabenende aktualisieren. Ein neuer Rechner muss allein mit dem Git-Stand, der Bauanleitung und den angegebenen öffentlich verfügbaren Werkzeugen weiterarbeiten können.
- Vollständigen Quellcode, Build-Skripte, erforderliche Ressourcen, eingebettete Laufzeitprogramme, deren Originalquellen und Lizenzen versionieren. Keine nur lokal vorhandenen Build-Zutaten voraussetzen. Externe Standardwerkzeuge mit Version und offiziellem Bezug dokumentieren.
- Neue IPKs erst hochladen, wenn der Nutzer genau diese Version persönlich getestet und ausdrücklich zur Veröffentlichung freigegeben hat. Agenten- und CI-Tests genügen nicht. Die erste angeforderte Veröffentlichung betrifft BoxSystemInfo 0.1.7.
- Vor jedem Push und jedem Release-Upload alle vorgesehenen Dateien einschließlich Archive und Archivmetadaten auf private Daten prüfen. `python3 tools/audit_upload.py` prüft den Git-Index; zusätzliche Release-Dateien als Argument übergeben. Verdachtsfunde vor Upload klären.
- Keine Zugangsdaten, privaten Netzadressen, lokalen Benutzernamen/-pfade, MAC-Adressen, Seriennummern, Receiver-Logs oder Screenshots mit Laufzeitdaten veröffentlichen. Persönliche Daten auch aus Archivmetadaten entfernen. Öffentliches Autorenkonto: Schrotty74.
- Projekt- und Buildpfade aus dem Checkout bzw. zur Laufzeit ermitteln. Keine persönlichen absoluten Pfade oder Box-Adressen fest eintragen. Notwendige Linux-Systempfade sind dokumentierte Schnittstellen und keine Projektpfade.
- Keine zusätzlichen Test-Apps oder globalen Umgebungsänderungen ohne ausdrücklichen Auftrag. Bestehende Dateien nicht nebenbei bereinigen. Eigene temporäre Dateien nach Verwendung entfernen.
- Aktuelles Plugin: [BoxSystemInfo-Regeln](context/BoxSystemInfo/AGENTS.md), [Bauanleitung](plugins/BoxSystemInfo/BUILDING.md).


- Ausnahme auf ausdrücklichen Nutzerauftrag: Die zwölf einzeln auf private Inhalte geprüften Screenshots zu 0.1.11 unter `plugins/BoxSystemInfo/docs/screenshots/` dürfen als Galerie veröffentlicht werden. Diese Ausnahme gilt nur für diese Aufnahmen; private Daten bleiben ausgeschlossen.

## Sprachen

`README.md` ist die englische Standardfassung, `README.de.md` die deutsche Fassung. Beide müssen sich gegenseitig verlinken und denselben fachlichen Stand beschreiben, sowohl im Repository-Stamm als auch pro Plugin. Changelogs ausschließlich auf Englisch in `CHANGELOG.md` führen; deutsche READMEs verlinken darauf. Beide Sprachfassungen bei Funktionsänderungen gemeinsam aktualisieren.

## Plugin-Seiten

Die Repository-Startseite bleibt ein kurzer Plugin-Katalog mit Icon, Kurzbeschreibung und Link. Ausführliche Angaben einschließlich Icon, Funktionen, Bedienung, Installation und Bauanleitung gehören auf die eigenen englischen/deutschen README-Seiten jedes Plugins. Bestehende Detailinformationen bei Sprachänderungen erhalten.
