# Box Systeminfo 0.1.7 für Enigma2

Box Systeminfo zeigt Receiver-, Speicher-, Temperatur- und Image-Daten auf einem Enigma2-Screen. Autor: Schrotty74. Ziel sind offene Enigma2-Images wie OpenPLi und OpenATV auf ARMv7-Receivern. Praktisch geprüft wurde die Vu+ Uno 4K SE mit OpenPLi scarthgap und Python 3.12.13.

## Oberfläche und Bedienung

Oben stehen drei Karten für Temperaturen, Arbeitsspeicher und freien Root-Speicher. Darunter folgen Receiver- und Image-Daten mit getrennten Beschriftungen und Werten. Die geladene Plugin-Version ist rechts oben sichtbar.

- Links/Rechts oder Grün: Theme wechseln. Midnight, Ocean, Amber und Light bleiben erhalten; die Auswahl wird gespeichert.
- OK: Werte aktualisieren.
- Exit oder Rot: Plugin schließen.
- Menü: Hilfe öffnen.

Abfragen erfolgen beim Öffnen und mit OK. Ein Theme-Wechsel startet keine Abfrage. Es gibt keinen Hintergrunddienst.

## Installation

Das IPK enthält das Plugin und ein statisch gebautes smartctl für ARMv7. Eine separate smartmontools-Installation ist nicht erforderlich. smartd, Autostart-Einträge, Firmware und Netzwerkeinstellungen werden nicht verändert.

```sh
opkg install /tmp/enigma2-plugin-extensions-boxsysteminfo_0.1.7_armv7ahf-neon.ipk
```

**Nach der Installation die Enigma2-Oberfläche (GUI) neu starten.** Erst dann wird die neue Plugin-Version geladen. Laufende Aufnahmen vor einem Neustart berücksichtigen.

Die Paketarchitektur `armv7ahf-neon` muss vom jeweiligen Image akzeptiert werden. Das mitgelieferte Werkzeug ist für 32-Bit-ARMv7-Linux gebaut, nicht für MIPS oder ein reines ARM64-System. Die statische Verknüpfung vermeidet eine Abhängigkeit von OpenPLi-Versionen der C/C++-Systembibliotheken. Image-Schnittstellen, Treiber und Paketarchitekturen können dennoch abweichen; eine Garantie für jedes offene Image besteht nicht. Python-2/3-kompatible Syntax wird angestrebt, Python 2 wurde nicht praktisch geprüft.

## SSD-Temperatur

smartctl 7.4 liegt im Plugin-Unterordner `bin/` und wird bevorzugt verwendet. Die Datei ist 897.240 Byte groß. Als Fallback sucht das Plugin auch im absoluten PATH und in üblichen Systemverzeichnissen. Es liest Attribute mit `smartctl -n standby,3 -A`, ohne SMART-Tests zu starten, SMART zu aktivieren oder Laufwerkseinstellungen zu ändern. Der Standby-Parameter soll das Aufwecken ruhender Laufwerke vermeiden; die Unterstützung hängt vom Gerät und dessen Anbindung ab.

Die Abfrage läuft über `eConsoleAppContainer` außerhalb des GUI-Threads. Ein Enigma2-Timer beendet einen Versuch nach drei Sekunden. Pro Aktualisierung gibt es höchstens vier Versuche. Fordert smartctl ausdrücklich einen Gerätetyp an, folgt ein begrenzter SAT-Versuch. Beim Schließen oder erneuten Aktualisieren wird die bisherige Abfrage abgebrochen. Passende hwmon-Sensoren dienen als Fallback.

Die Anzeige unterscheidet unter anderem fehlendes Werkzeug, Standby, Zeitüberschreitung und fehlende Temperaturdaten. Ein fehlender Wert bedeutet nicht, dass das Laufwerk keinen Sensor hat. Bei mehreren Laufwerken erscheint die erste verfügbare Temperatur. Die Kartenansicht zeigt den Temperaturwert ohne Gerätenamen.

Auf der untersuchten Box fehlten ursprünglich smartctl und hddtemp. Ein freigegebener Diagnose-Aufruf aus dem offiziellen OpenPLi-Paket lieferte aus ATA-Attribut 194 einen gültigen Wert von 35 °C mit Rückgabecode 0. Der alte Parser konnte diese Tabellenzeile bereits lesen; Ursache war das fehlende Werkzeug. Für die Integration wurde smartctl anschließend aus dem Originalquellcode statisch für ARMv7 gebaut.

## Image-Versionen

Die Erkennung verwendet optional `Components.SystemInfo.BoxInfo` und `boxbranding` sowie `/usr/lib/enigma.info`, `/etc/image-version`, `/etc/os-release` und als Namensfallback `/etc/issue`. Version, Build und vorhandenes Erstellungsdatum werden getrennt angezeigt. Fehlende Werte bleiben als „—“ sichtbar.

Die tatsächlichen Werte auf der untersuchten Box sind `OpenPLi`, Image-Version `scarthgap`, Build/Revision `c09e297d` und Erstellungsdatum `11.10.2026`. Eine zusätzliche numerische Image-Nummer wurde in den geprüften Quellen nicht gefunden. Die Enigma2-Version stammt bevorzugt aus `enigma.getEnigmaVersionString()`, ersatzweise aus der About-Schnittstelle. `/etc/version` wird dafür nicht mehr verwendet.

Referenzen: [OpenPLi BoxInfo](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/python/Components/SystemInfo.py), [OpenPLi About](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/python/Components/About.py), [OpenWebif Image-Erkennung](https://github.com/oe-alliance/OpenWebif/blob/main/plugin/controllers/models/info.py), [Enigma2 Prozessverwaltung](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/base/console.cpp).

## Paket bauen und prüfen

Die vollständige Anleitung für einen frischen Rechner steht in [BUILDING.md](BUILDING.md).

```sh
./build.sh
python3 -B -m unittest discover -s tests -v
```

Der Paketbau benötigt Python 3 und tar. Das Build-Skript übernimmt das vorhandene ARMv7-Programm, erzeugt ein opkg-kompatibles ar-Archiv unter `dist/` und entfernt temporäre Build-Dateien. Die Regressionstests prüfen Temperaturparser, Image-Fallbacks und den Ablauf asynchroner Abfragen mit Enigma2-Testdoubles.

Zum erneuten Übersetzen von smartctl werden Zig 0.14.1, make und die configure-Dateien im mitgelieferten Originalquellarchiv benötigt:

```sh
ZIG="$(command -v zig)" ./tools/build-smartctl.sh
./build.sh
```

Das vollständige Quellcode-ZIP enthält Plugin-Code, Tests, beide Build-Skripte, Originalquellcode und Lizenztexte. Herkunft, Build-Parameter und Prüfsummen stehen unter `src/usr/share/doc/boxsysteminfo/smartmontools/HERKUNFT.md`. Die Quell- und Lizenzdateien sind auch im IPK enthalten.

## Geprüfter Stand

19 Regressionstests sind bestanden. Python-3.12-Syntax auf der Box, Shell-Syntax, Skin-XML, Versionsangaben und vollständiger IPK-Inhalt wurden geprüft. Das eingebettete ARM-Programm wurde als statisch verknüpft ohne dynamischen Programmlader geprüft; seine Prüfsumme stimmt mit der installierten Datei überein.

0.1.6 wurde auf der Uno 4K SE installiert und nach freigegebenem GUI-Neustart geöffnet. Die SSD-Temperatur erschien mit 37 °C. Image-Version, Build und Enigma2-Version sind sichtbar. Alle vier Themes wurden visuell geprüft; Aktualisieren, Schließen während einer Abfrage und erneutes Öffnen funktionierten. Zeitüberschreitungen und Prozessfehler wurden mit Testdoubles geprüft, nicht durch absichtlich blockierte Box-Laufwerke.

OpenATV, andere Receiver und Python 2 wurden nicht praktisch geprüft. Die Unterstützung bleibt dafür angestrebt, ohne pauschale Kompatibilitätszusage.

0.1.7 wurde anschließend installiert. Icon-Verknüpfung, transparentes PNG-Format, Paketinhalt und Übereinstimmung der installierten Dateien wurden geprüft. Das neue Icon ist im Plugin-Menü der Box sichtbar. Die Bildquelle und der verwendete Imagegen-Prompt liegen unter `artwork/`.

## Updates

Es gibt keinen festen Veröffentlichungsrhythmus und keine automatische Update-Quelle für dieses Projekt. Neue Plugin-Pakete werden bei Bedarf erstellt und können eine neuere geprüfte smartctl-Version enthalten. Die bisher einzeln abgelegte Diagnose-Datei nahm nicht an opkg-Updates teil; das integrierte Werkzeug gehört nun zum Plugin-Paket. Das Plugin lädt selbst keine neuen Programme herunter.

## Versionen

- 0.1.7: Eigenes transparentes Receiver-Icon für den Plugin-Menüeintrag.

- 0.1.6: Vollständiges Neuzeichnen beim Theme-Wechsel und passende Texthintergründe für die Karten.

- 0.1.5: smartctl statisch für ARMv7 integriert, mit Originalquellcode und Lizenzen; Abschnittsüberschriften über den Kartenhintergründen angeordnet.
- 0.1.4: Karten für Temperatur, RAM und Root-Speicher; getrennte Beschriftungen und Werte.
- 0.1.3: SMART-Abfrage asynchron mit Zeitlimit und Statusmeldungen; PATH-Suche und weitere Temperaturformate; Image-Version und Build aus zusätzlichen Quellen; echtes Enigma2-Versions-API; sichtbare Plugin-Version und Image-Erstellungsdatum.
- 0.1.2: Laufwerkstemperatur zusätzlich aus SMART-Werten lesen.
- 0.1.1: Vu+-Modellkennung priorisiert; Temperaturwerte für SoC und SSD ergänzt.
- 0.1.0: Erste Testversion mit Systeminformationen und Themes.

## Lizenz

Der Plugin-Code steht unter MIT, siehe LICENSE. Für smartctl gilt GPL Version 2; die statisch eingebundenen Laufzeiten haben eigene Lizenztexte im oben genannten Dokumentationsordner.
