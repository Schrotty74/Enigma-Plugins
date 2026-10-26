# BoxSystemInfo: Projektkontext

## Projekt

Enigma2-Systeminfo-Plugin von Schrotty74 im Repository `Schrotty74/Enigma-Plugins`. Vollständiger Plugin-Bestand unter `plugins/BoxSystemInfo/`; dieser Kontext liegt getrennt unter `context/BoxSystemInfo/`.

## Stand 0.1.9

- Die allgemeine Kartenübersicht ist weiterhin der Startbildschirm: Temperaturen, RAM, Root-Speicher, Receiver und Image-Daten.
- Gelb öffnet Details zu Aufnahmespeicher/SSD, CPU, Netzwerk und Tuner/Aufnahmen. Hoch/Runter bzw. Gelb/Blau blättert, Exit kehrt zur Übersicht zurück. Links/Rechts bzw. Grün wechselt das gespeicherte Theme.
- Aufnahmespeicher zeigt Kapazität, belegten/freien Platz und Belegung. Bei fehlendem konfiguriertem Pfad wird ein eindeutig eingehängter Enigma2-Datenträger verwendet; mehrere unklare Datenträger werden nicht geraten.
- SSD-Details: Modell, SMART-Gesamtstatus und Betriebsstunden, soweit verfügbar. Nur lesende Abfragen mit Zeitlimit, keine SMART-Tests oder Laufwerkseinstellungen.
- CPU-Kerne und Takt, Systemlast-Mittelwerte, Netzwerk-Verbindung/Linkgeschwindigkeit sowie erkannte Tuner-Nutzung und Aufnahmezähler ergänzen die Anzeige. FBC kann virtuelle Frontends melden; nicht erkannte Aktivität bedeutet nicht automatisch frei.
- Hinweisfarben: SoC ab 80 °C, Laufwerk ab 60 °C, Speicherbelegung ab 90 % sowie SMART-Fehler und nur lesbarer Aufnahmespeicher. Das sind Hinweisschwellen, keine Herstellergrenzwerte.

## Tests und Freigabe

48 Regressionstests, Python-3.12-Syntax, Shell-Syntax und Paketbau sind geprüft. Die installierten geänderten Quelldateien stimmen mit dem Repository überein. Das abschließende 0.1.9-IPK ist bytegleich mit dem auf dem Receiver installierten Testpaket.

Der Nutzer hat bestätigt, dass die fehlenden Speicherwerte in 0.1.9 angezeigt werden, und den IPK-Upload ausdrücklich beauftragt. Für 0.1.9 liegt damit die persönliche Testbestätigung und Freigabe vor. Jede spätere IPK-Version benötigt eine neue Bestätigung und Freigabe.

0.1.7 ist als früheres Release unter `boxsysteminfo-v0.1.7` erhalten. Die Erweiterungsserie wurde auf `development/boxsysteminfo-0.1.8` entwickelt; aktueller Release-Tag ist `boxsysteminfo-v0.1.9`. Den tatsächlichen Branch-/Tag-/Release-Stand bei Fortsetzung mit Git/GitHub prüfen.

## Nachbauen und Grenzen

Originalquelle smartmontools 7.4, statisches ARMv7-Programm, Lizenzen und Build-Skripte sind vollständig versioniert. Quelle unter `src/usr/share/doc/boxsysteminfo/smartmontools/` hat SHA256 `e9a61f641ff96ca95319edfb17948cd297d0cd3342736b2c49c99d4716fb993d`.

smartctl wird mit Zig 0.14.1 für `arm-linux-musleabihf`, CPU `generic+v7a+vfp3d16`, gebaut. Bauanleitung: `plugins/BoxSystemInfo/BUILDING.md`. Praktisch geprüft: OpenPLi auf Vu+ Uno 4K SE. OpenATV, weitere Receiver und Python 2 sind ungeprüft. Ein frischer Mac-End-to-End-Build und byte-identische Neubauten des smartctl-Programms sind nicht nachgewiesen.

## Verbindliche Pflege

Keine privaten Daten oder persönlichen festen Pfade in Git oder Upload-Artefakten. Jede Upload-Auswahl einschließlich Archive/Metadaten prüfen. Englisch ist der README-Standard, Deutsch eine gegenseitig verlinkte Fassung; Changelogs nur Englisch. Alle vier Kontextdateien nach wesentlichen Änderungen und zum Abschluss aktualisieren.
