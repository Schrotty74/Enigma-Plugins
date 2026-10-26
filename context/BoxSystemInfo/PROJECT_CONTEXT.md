# BoxSystemInfo: Projektkontext

## Zweck

BoxSystemInfo ist ein Enigma2-Plugin für Systeminformationen auf Receivern. Die öffentliche Zuordnung lautet Autor `Schrotty74`, Repository `Schrotty74/Enigma-Plugins`.

## Verlässlicher Stand

- Stabiler Ausgangspunkt: Version 0.1.7 auf `main`.
- Release-Tag: `boxsysteminfo-v0.1.7`.
- Die genaue 0.1.7-Quelle stammt aus dem zugehörigen installierten Paket und dem vorhandenen vollständigen Quellenbestand. Dieser Stand ist die Basis für weitere Arbeiten.
- Sechs beauftragte Änderungen für 0.1.8 werden anschließend auf `development/boxsysteminfo-0.1.8` umgesetzt.
- Ein 0.1.8-IPK darf erst nach eigenem Test durch den Nutzer und dessen ausdrücklicher Freigabe veröffentlicht werden. Tests durch einen Agenten genügen dafür nicht.

## Lieferumfang im Plugin-Verzeichnis

`plugins/BoxSystemInfo/` muss als eigenständiger, vollständiger Plugin-Bestand im Git-Repository liegen. Dazu gehören:

- installierbarer Plugin-Quellcode und Runtime-Dateien, einschließlich des vorhandenen Runtime-Binaries;
- alle Build-Skripte und Hilfsdateien;
- die Originalquellen von Smartmontools 7.4;
- die zugehörigen Lizenztexte unter `src/usr/share/doc/boxsysteminfo/smartmontools/`.

Die Smartmontools-7.4-Quelldatei hat den erwarteten SHA-256-Wert:

`e9a61f641ff96ca95319edfb17948cd297d0cd3342736b2c49c99d4716fb993d`

## Build-Ziele und Grenzen

- Das Runtime-Binary wird mit Zig 0.14.1 für `arm-linux-musleabihf` erstellt; die Skriptkonfiguration zielt auf `generic+v7a+vfp3d16`.
- Ziel sind ARMv7-Enigma2-Images, insbesondere OpenPLi und OpenATV. Bisher ist nur ein Zielsystem verifiziert.
- Es gibt keinen Nachweis für byte-identische Builds und keinen abgeschlossenen End-to-End-Build auf einem frischen Mac.
- Dokumentation muss genau zwischen Skriptkonfiguration, tatsächlich geprüften Systemen und noch ungeprüften Plattformen unterscheiden.

## Datenschutz und Portabilität

Keine lokalen absoluten Pfade, privaten IP-Adressen, Passwörter, Benutzernamen, MAC-Adressen, Seriennummern oder Screenshots in Git aufnehmen. Dokumentation und Build-Anleitungen verwenden relative Repository-Pfade. Keine Werkzeuge systemweit installieren und keine globale Entwicklungsumgebung ändern.

## Kontextpflege

Nach jeder wesentlichen Änderung und zum Aufgabenabschluss die Kontextdokumente aktualisieren. `NEXT_STEPS.md` enthält offene Arbeit; abgeschlossene Punkte daraus entfernen oder als erledigt kennzeichnen.

## Erstveröffentlichung 0.1.7

Der Nutzer hat den Upload des letzten fertigen IPKs ausdrücklich beauftragt. Für den ersten öffentlichen Upload werden ausschließlich die Archivmetadaten neutralisiert; installierbare Dateien und Steuerdaten bleiben bytegleich mit dem bisherigen lokalen 0.1.7-Paket. Der vollständige Paketquellcode und der bereinigte Paketbau gehören zum Release-Tag. Die neue Funktionsversion 0.1.8 hat keine Veröffentlichungsfreigabe.
