# Startvorlage für BoxSystemInfo

Arbeite am Enigma2-Plugin BoxSystemInfo im Repository `Schrotty74/Enigma-Plugins` weiter.

Lies zuerst `AGENTS.md` im Repository-Stamm sowie alle vier Dateien unter `context/BoxSystemInfo/`. Für Build-Arbeit zusätzlich `plugins/BoxSystemInfo/BUILDING.md` lesen. Prüfe Git-Status, Branches und vollständige betroffene Dateien; schlage keine schon vorhandenen Funktionen erneut vor.

Aktueller Release-Stand ist 0.1.11 auf `main`, Tag `boxsysteminfo-v0.1.11`. Der Nutzer hat das installierte Paket erfolgreich getestet und den Upload mit ausführlichem englischen Changelog ausdrücklich beauftragt. 95 Tests und die Receiver-Prüfung einschließlich englischer Verlaufsansicht, Diagnoseexport und Update-Hinweis sind erfolgreich. Das öffentliche IPK ist das unveränderte getestete Paket mit SHA256 `dbc83716e920e190f4b6c03633dd75435e9e981b2711c5b5e8994d3ebad6f71b`. 0.1.10 wurde nicht separat veröffentlicht; seine Änderungen sind in 0.1.11 enthalten.

0.1.11 ergänzt Verlaufskurven im Sitzungs-RAM, drei konfigurierbare Startkarten, Warnschwellen, RAM-/Swap-Details, einen ausschließlich manuell erzeugten Diagnosebericht und eine ausschließlich manuelle Update-Prüfung. Eine Laufwerksauswahl ist ausdrücklich nicht beauftragt. Alle bisherigen Funktionen und die allgemeine Startübersicht bleiben erhalten.

Die allgemeine Übersicht bleibt der Startbildschirm. Gelb öffnet zusätzliche Details, Exit führt zurück. Der Nutzer hat 0.1.11 bestätigt und den Upload ausdrücklich freigegeben. Für spätere IPKs ist erneut sein persönlicher Test und eine ausdrückliche Veröffentlichungsfreigabe nötig.

Halte alle Quellen, Ressourcen, Build-Skripte, eingebetteten Programme, Originalquellen und Lizenzen in Git. Projektpfade relativ oder zur Laufzeit ermitteln. Box-Zugänge lokal neu bereitstellen; keine privaten Daten, lokalen Benutzerpfade oder Receiver-Screenshots veröffentlichen. Vor jedem Upload die konkreten Git-Dateien und Artefakte samt Archivmetadaten mit `tools/audit_upload.py` und inhaltlich prüfen.

README.md ist Englisch, README.de.md Deutsch; beide verlinken sich gegenseitig. Changelogs bleiben ausschließlich Englisch. Keine globalen Installationen oder zusätzlichen Test-Apps ohne Auftrag, keine ungeprüften Kompatibilitäts- oder Nachbaubarkeitsversprechen. Kontextdateien nach wesentlichen Änderungen und zum Abschluss aktualisieren.

## README-Aufteilung

Die Repository-Startseite bleibt ein kurzer Plugin-Katalog mit Icon, Kurzbeschreibung und Link. Ausführliche Angaben einschließlich Icon, Funktionen, Bedienung, Installation und Bauanleitung gehören auf die eigenen englischen/deutschen README-Seiten jedes Plugins. Bestehende Detailinformationen bei Sprachänderungen erhalten.

Die englische und deutsche Bildergalerie liegen unter `plugins/BoxSystemInfo/GALLERY.md` und `GALLERY.de.md`. Die zwölf Bilder unter `docs/screenshots/` sind auf ausdrücklichen Nutzerauftrag für die Veröffentlichung geprüft. Die übrigen Datenschutzregeln gelten unverändert.
