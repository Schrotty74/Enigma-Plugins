# BoxSystemInfo: Arbeitsregeln

Diese Datei gilt für `plugins/BoxSystemInfo/` und `context/BoxSystemInfo/`.

## Branches und Releases

- `main` enthält den stabilen Stand 0.1.7. Der Release-Tag lautet `boxsysteminfo-v0.1.7`.
- Arbeiten an den sechs geplanten Änderungen für 0.1.8 gehören später auf `development/boxsysteminfo-0.1.8`.
- Keine 0.1.8-IPK hochladen oder veröffentlichen, bevor der Nutzer die Version selbst getestet und ausdrücklich freigegeben hat. Agententests ersetzen diese Freigabe nicht.
- Kontextdokumente nach jeder wesentlichen Änderung und am Ende einer Aufgabe aktualisieren.

## Vollständige, portable Quellen

- Das Plugin-Verzeichnis muss den vollständigen Quellcode, Build-Skripte, die originale Smartmontools-7.4-Quellarchivdatei und die zugehörigen Lizenzen enthalten.
- Smartmontools-Quellarchiv und Lizenzdateien liegen unter `src/usr/share/doc/boxsysteminfo/smartmontools/`.
- Der Git-Stand muss den Runtime-Binary-Bestand und die Quellen samt Build-Werkzeugen umfassen.
- Builds müssen aus einem frischen Checkout auf macOS und Linux ohne persönliche absolute Pfade funktionieren. Keine privaten IP-Adressen, Passwörter, Benutzernamen, MAC-Adressen, Seriennummern oder Screenshots einchecken.
- Pfade in der Dokumentation relativ zum Repository angeben. Keine zusätzlichen Test-Apps oder globalen Werkzeug-/Umgebungsänderungen anlegen.

## Build und Verifikation

- Den lokalen Build-Ablauf in `plugins/BoxSystemInfo/BUILDING.md` dokumentieren und einhalten.
- Für Smartmontools ist Zig 0.14.1 vorgesehen. Das Build-Skript erhält den Zig-Pfad über `ZIG`; Werkzeuge nicht automatisch installieren.
- Ergebnisse, die nicht tatsächlich geprüft wurden, nicht als reproduzierbar oder plattformübergreifend getestet bezeichnen.
- Für Python-Tests: `python3 -B -m unittest discover -s tests -v`.
