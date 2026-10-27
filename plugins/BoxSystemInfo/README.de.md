# Box Systeminfo 0.1.11 lokaler Testbuild für Enigma2

[English](README.md) · [Deutsch](README.de.md) · [Changelog (English)](CHANGELOG.md) · [Bauanleitung](BUILDING.md)

![Box Systeminfo](src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/icon.png)

Box Systeminfo zeigt Receiver-, Speicher-, Temperatur- und Image-Daten auf einem Enigma2-Bildschirm. Autor ist Schrotty74. Das Plugin richtet sich an offene Enigma2-Images wie OpenPLi und OpenATV auf ARMv7-Receivern. Version 0.1.9 wurde auf dem Receiver des Nutzers getestet. Der Nutzer bestätigte, dass die Daten jetzt angezeigt werden, und gab die Veröffentlichung des IPK frei.

Diese Seite beschreibt auch den lokalen Testbuild 0.1.11. Version 0.1.9 bleibt das neueste öffentliche IPK. Der Nutzer hat 0.1.10 erfolgreich getestet, aber noch nicht zur Veröffentlichung freigegeben. Version 0.1.11 besteht 95 Tests und ist auf dem Receiver installiert; die GUI-Prüfung läuft. Die Version ist nicht veröffentlicht.

## Bildschirm und Bedienung

Die Startansicht zeigt Karten für Temperaturen, Arbeitsspeicher und freien Root-Speicher. Darunter folgen Receiver- und Image-Daten. Rechts oben steht die geladene Plugin-Version.

- Links/Rechts oder Grün: Theme wechseln. Midnight, Ocean, Amber und Light stehen zur Wahl; die Auswahl wird gespeichert.
- OK: Werte aktualisieren.
- Exit oder Rot: Plugin schließen.
- Gelb oder Blau: Details öffnen.
- In den Details blättern Hoch/Runter oder Gelb/Blau durch Speicher/SSD, CPU, Netzwerk und Tuner. Exit führt zurück zur Startübersicht.
- Menü: Aktualisierungsintervall, Sprache, Übersichtskarten, Warnschwellen und Verlaufskurven einstellen, manuell nach einer freigegebenen Version suchen, einen Diagnosebericht exportieren oder die Hilfe öffnen. Zur Wahl stehen Aus, 2, 5, 10 und 30 Sekunden; standardmäßig sind es 5 Sekunden. Die drei Übersichtskarten lassen sich jeweils mit Temperatur, RAM, Root-Speicher, Aufnahmespeicher oder Netzwerk belegen. Die Voreinstellungen bleiben erhalten. Wird eine bereits verwendete Karte gewählt, tauschen die Belegungen. Die Auswahl wird gespeichert.

Automatische Aktualisierungen laufen nur, solange das Plugin geöffnet ist. OK aktualisiert sofort. Bei automatischen Aktualisierungen werden SMART-Daten höchstens einmal in 60 Sekunden abgefragt; OK startet eine neue SMART-Abfrage. Ein Theme-Wechsel startet keine neue Abfrage. Es gibt keinen Hintergrunddienst. Die Sprache folgt nach Möglichkeit der Image-Einstellung und fällt andernfalls auf Englisch zurück. Über das Menü lässt sie sich ändern.

## Installation

Das IPK enthält das Plugin und ein statisch gebautes `smartctl` für ARMv7. Eine separate smartmontools-Installation ist nicht nötig. Das Plugin installiert weder `smartd` noch Autostart-Einträge und ändert weder Firmware noch Netzwerkeinstellungen.

```sh
opkg install /tmp/enigma2-plugin-extensions-boxsysteminfo_0.1.9_armv7ahf-neon.ipk
```

**Nach der Installation die Enigma2-Oberfläche (GUI) neu starten.** Erst danach wird die neue Plugin-Version geladen. Laufende Aufnahmen vor dem Neustart berücksichtigen.

Das Image muss die Paketarchitektur `armv7ahf-neon` akzeptieren. Das mitgelieferte Werkzeug ist für 32-Bit-ARMv7-Linux gebaut, nicht für MIPS oder ein reines ARM64-System. Durch statische Verknüpfung hängt es nicht von den Versionen der C/C++-Systembibliotheken des Images ab. Image-Schnittstellen, Treiber und Paketarchitekturen können trotzdem abweichen. Eine Garantie für jedes offene Image gibt es nicht. Der Python-Code verwendet Syntax, die mit Python 2 und 3 kompatibel sein soll; Python 2 wurde auf einem Receiver nicht praktisch geprüft.

## SSD-Temperatur und SMART-Details

Das Plugin bevorzugt das mitgelieferte smartctl 7.4 im Ordner `bin/`. Die Binärdatei ist 897.240 Byte groß. Als Fallback durchsucht das Plugin `PATH` und übliche Systemverzeichnisse. Mit `smartctl -n standby,3 -i -H -A` liest es Informationen aus. SMART-Tests werden nicht gestartet, SMART wird nicht aktiviert und Laufwerkseinstellungen werden nicht geändert. Die Standby-Option soll verhindern, dass ein ruhendes Laufwerk aufwacht; ihre Unterstützung hängt vom Gerät und Anschluss ab.

Die Detailansicht zeigt außerdem, soweit verfügbar, Laufwerksmodell, SMART-Gesamtstatus und Betriebsstunden. Seriennummern werden nicht angezeigt.

SMART-Details zeigen freigegebene Verschleiß- und Fehlerzähler, sofern das Laufwerk sie bereitstellt: remappte, ausstehende, offline nicht korrigierbare, gemeldete nicht korrigierbare, Ende-zu-Ende-, CRC-, Programmier- und Löschfehler. Verfügbarer Reservespeicher, ausdrücklich als verbleibender Prozentwert bezeichnete Lebensdauer, Host-Schreibmenge in GiB sowie TLC-/SLC-NAND-Schreibmenge können ebenfalls erscheinen. Aus `Wear_Leveling_Count` oder `Media_Wearout_Indicator` wird keine Restlebensdauer abgeleitet. Die vorliegenden WD-Attribute liefern keinen sicheren Restlebensdauer-Prozentwert.

Abfragen laufen über `eConsoleAppContainer` außerhalb des GUI-Threads. Ein Enigma2-Timer begrenzt jeden Versuch auf drei Sekunden; pro Aktualisierung gibt es höchstens vier Versuche. Fordert smartctl ausdrücklich einen Gerätetyp an, folgt ein begrenzter SAT-Versuch. Beim Schließen oder erneuten Aktualisieren wird die laufende Abfrage abgebrochen. Ein passender hwmon-Sensor dient als Fallback.

Die Anzeige unterscheidet unter anderem fehlendes Werkzeug, Standby, Zeitüberschreitung und fehlende Temperaturdaten. Ein fehlender Wert beweist nicht, dass ein Laufwerk keinen Sensor besitzt. Bei mehreren Laufwerken erscheint die erste verfügbare Temperatur. Auf der Startkarte wird kein Gerätename angezeigt.

## Weitere Details

- Aufnahmespeicher: Kapazität, belegter und freier Platz, prozentuale Belegung und Einhängepunkt. Vorrang hat der konfigurierte Aufnahmepfad. Ist keiner gesetzt, verwendet das Plugin eine von Enigma2 eingehängte Partition nur dann, wenn genau ein Kandidat gefunden wird. Bei mehreren möglichen Partitionen bleibt der Pfad offen. Ein nicht eingehängter Aufnahmeordner wird nicht als Speicherlaufwerk angezeigt.
- Die Speicherabfrage läuft in einem eigenen Python-Prozess mit drei Sekunden Zeitlimit. Langsame Netzwerkdateisysteme blockieren dadurch nicht die Oberfläche.
- CPU: Anzahl aktiver Kerne, aktueller und maximaler Takt, soweit verfügbar, sowie Systemlast über 1, 5 und 15 Minuten. Systemlast ist keine prozentuale CPU-Auslastung.
- Netzwerk: Schnittstelle, Typ, Verbindungsstatus, ausgehandelte Linkgeschwindigkeit, sofern der Treiber sie bereitstellt, und Empfangs-/Senderaten in Mbit/s. Raten erscheinen nach zwei Zählerständen. Es erfolgen keine Internetabfragen. IP- und MAC-Adressen werden nicht angezeigt.
- Tuner: konfigurierte Frontends und erkannte aktive Nutzung. Der aktive DVB-Dienst kann zusätzlich Signalqualität in dB oder als treiberabhängigen Prozentwert, relative Signalstärke (AGC), BER und Lock-Status melden. Nicht unterstützte Werte bleiben nicht verfügbar. FBC-Tuner können virtuelle Frontends liefern. Ein nicht beobachteter Tuner wird nicht als frei ausgegeben. Echte Aufnahmen werden nach Möglichkeit gefiltert; ein Zähler aus der Timerliste wird entsprechend bezeichnet.
- Hinweise: SoC-Schwellen von 60 bis 95 °C in 5-Grad-Schritten (Standard 80 °C), Laufwerksschwellen von 40 bis 70 °C in 5-Grad-Schritten (Standard 60 °C) sowie RAM- und Speichergrenzen von 75, 80, 85, 90, 95 oder 98 % (Standard 90 %). SMART-Fehler und ein nur lesbarer Aufnahmespeicher werden ebenfalls hervorgehoben. Die Anzeige ist ein visueller Hinweis, keine Herstellergrenze.

Die Tuneransicht erkennt möglicherweise nicht jede aktive Nutzung, etwa alle Streaming- oder Bild-in-Bild-Dienste. „Keine aktive Nutzung erkannt“ bedeutet deshalb nicht, dass ein Tuner sicher frei ist.

## Verlauf, Übersichtskarten und Diagnose

Die optionalen Verlaufskurven zeigen die letzten zehn Minuten der SoC- und SSD-Temperatur sowie Empfangs- und Senderaten der aktuell ausgewählten aktiven Netzwerkschnittstelle. SSD-Werte werden bei automatischer Aktualisierung nur übernommen, wenn die letzte Laufwerksmessung höchstens 60 Sekunden alt ist. Für die Kurve wird das Laufwerk nicht zusätzlich abgefragt. Der Verlauf besteht nur während der geöffneten Plugin-Sitzung und wird beim Schließen gelöscht; er wird nicht dauerhaft gespeichert. Die Ansicht öffnet sich über den Menüpunkt **Verlaufskurven**.

Die RAM-Details zeigen Gesamt-, verfügbaren, belegten und freien Speicher sowie Cache, Puffer und Swap. Der verfügbare Speicher enthält rückgewinnbaren Speicher und darf nicht zu Cache und Puffern addiert werden.

**Diagnosebericht exportieren** ist ein manueller Menüpunkt. Er schreibt eine numerische Positivliste und die Plugin-Version als JSON-Datei in das temporäre Laufzeitverzeichnis, mit Dateimodus 0600. IP- und MAC-Adressen, Seriennummern, Hostnamen, lokale Pfade, Protokolle und Zugangsdaten sind nicht enthalten. Das Plugin lädt die Datei nicht hoch.

**Nach Updates suchen** ist ebenfalls ein manueller Menüpunkt. Er prüft Metadaten veröffentlichter, nicht als Vorabversion markierter ARMv7-Pakete im offiziellen GitHub-Repository. Release-Dateien werden weder heruntergeladen noch installiert. Die Netzwerkanfrage läuft außerhalb des GUI-Threads und hat ein Zeitlimit.

## Image- und Enigma2-Versionen

Die Erkennung verwendet optional `Components.SystemInfo.BoxInfo` und `boxbranding`. Zusätzlich prüft sie `/usr/lib/enigma.info`, `/etc/image-version`, `/etc/os-release` und als Namensfallback `/etc/issue`. Image-Version, Build und vorhandenes Erstellungsdatum erscheinen getrennt. Fehlende Werte bleiben als `—` sichtbar.

Die Enigma2-Version stammt bevorzugt aus `enigma.getEnigmaVersionString()`, ersatzweise aus der About-Schnittstelle. `/etc/version` wird dafür nicht verwendet.

Referenzen: [OpenPLi BoxInfo](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/python/Components/SystemInfo.py), [OpenPLi About](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/python/Components/About.py), [OpenWebif Image-Erkennung](https://github.com/oe-alliance/OpenWebif/blob/main/plugin/controllers/models/info.py), [Enigma2 Prozessverwaltung](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/base/console.cpp).

## Build und Tests

Die vollständige Anleitung steht in [BUILDING.md](BUILDING.md).

```sh
./build.sh
python3 -B -m unittest discover -s tests -v
```

Der Paketbau verwendet Python 3 und `tar`. Das Skript übernimmt das vorhandene ARMv7-Programm, erstellt unter `dist/` ein opkg-kompatibles ar-Archiv und entfernt temporäre Build-Dateien. Die Tests prüfen Temperaturparser, Image-Fallbacks, Speichermounts, SMART-Felder, Warnschwellen, Prozessabbruch und Bildschirm-Lebenszyklus mit Enigma2-Testdoubles.

Für einen Neubau von smartctl werden Zig 0.14.1, `make` und die Configure-Dateien aus dem mitgelieferten Quellarchiv benötigt:

```sh
ZIG="$(command -v zig)" ./tools/build-smartctl.sh
./build.sh
```

Das Quellarchiv enthält Plugin-Code, Tests, Build-Skripte, die Originalquellen von smartmontools und Lizenzdateien. Herkunft, Build-Parameter und Prüfsummen stehen in `src/usr/share/doc/boxsysteminfo/smartmontools/HERKUNFT.md`. Quell- und Lizenzdateien sind auch im IPK enthalten.

## Kompatibilität und Prüfungen

OpenPLi und OpenATV sind Ziel-Images. Praktisch geprüft wurde bisher eine Receiver-/Image-Kombination. OpenATV, andere Receiver und Python 2 wurden nicht auf Hardware getestet. Eine allgemeine Kompatibilitätszusage gibt es nicht. Zeitüberschreitungen und Prozessfehler werden mit Testdoubles geprüft, nicht durch absichtlich blockierte Laufwerke auf dem Receiver.

Der lokale Testbuild 0.1.10 besteht 67 Tests und ist auf dem Receiver installiert. Die installierten Python-Quellen wurden mit dem damaligen Checkout abgeglichen. Übersicht, Detailseiten, Sprachwahl und Aktualisierungsoptionen wurden auf dem Receiver geprüft. Der Nutzer bestätigte, dass 0.1.10 funktioniert; die Veröffentlichungsfreigabe steht noch aus. Version 0.1.11 besteht 95 Tests und ist als unveröffentlichter lokaler Testbuild installiert. Die GUI-Prüfung läuft; persönlicher Nutzertest und Veröffentlichungsfreigabe stehen aus.

Die aktuelle Version ist 0.1.9. Frühere Änderungen stehen im englischen [Changelog](CHANGELOG.md). Der Quellcode-Tag heißt `boxsysteminfo-v0.1.9`.

## Updates

Das Menü bietet eine optionale manuelle Suche nach veröffentlichten Versionen. Sie liest Release-Metadaten aus dem offiziellen GitHub-Repository, berücksichtigt veröffentlichte ARMv7-Pakete ohne Vorabversion und lädt keine Pakete herunter oder installiert sie. Automatische Prüfungen finden nicht statt.

## Lizenz

Der Plugin-Code steht unter MIT; siehe `LICENSE`. Für smartctl gilt GPL Version 2. Die statisch eingebundenen Laufzeiten haben eigene Lizenztexte im oben genannten Dokumentationsordner.
