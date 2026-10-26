# Startvorlage für BoxSystemInfo

Arbeite am Enigma2-Plugin BoxSystemInfo im Repository `Schrotty74/Enigma-Plugins` weiter.

Lies zuerst `AGENTS.md` im Repository-Stamm sowie alle vier Dateien unter `context/BoxSystemInfo/`. Für Build-Arbeit zusätzlich `plugins/BoxSystemInfo/BUILDING.md` lesen. Prüfe Git-Status, Branches und vollständige betroffene Dateien; schlage keine schon vorhandenen Funktionen erneut vor.

Aktueller geprüfter und zur Veröffentlichung freigegebener Stand ist 0.1.9, Tag `boxsysteminfo-v0.1.9`; 0.1.7 bleibt als älteres Release erhalten. Die Erweiterungen entstanden auf `development/boxsysteminfo-0.1.8`. Prüfe den aktuellen GitHub-Stand statt einen Branch blind vorauszusetzen.

Die allgemeine Übersicht bleibt der Startbildschirm. Gelb öffnet zusätzliche Details, Exit führt zurück. Der Nutzer hat die korrigierten Speicherwerte in 0.1.9 bestätigt und den Upload ausdrücklich freigegeben. Für spätere IPKs ist erneut sein persönlicher Test und eine ausdrückliche Veröffentlichungsfreigabe nötig.

Halte alle Quellen, Ressourcen, Build-Skripte, eingebetteten Programme, Originalquellen und Lizenzen in Git. Projektpfade relativ oder zur Laufzeit ermitteln. Box-Zugänge lokal neu bereitstellen; keine privaten Daten, lokalen Benutzerpfade oder Receiver-Screenshots veröffentlichen. Vor jedem Upload die konkreten Git-Dateien und Artefakte samt Archivmetadaten mit `tools/audit_upload.py` und inhaltlich prüfen.

README.md ist Englisch, README.de.md Deutsch; beide verlinken sich gegenseitig. Changelogs bleiben ausschließlich Englisch. Keine globalen Installationen oder zusätzlichen Test-Apps ohne Auftrag, keine ungeprüften Kompatibilitäts- oder Nachbaubarkeitsversprechen. Kontextdateien nach wesentlichen Änderungen und zum Abschluss aktualisieren.
