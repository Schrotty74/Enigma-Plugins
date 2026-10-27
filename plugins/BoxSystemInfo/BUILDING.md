# BoxSystemInfo bauen

Diese Anleitung beschreibt den vorgesehenen Build-Ablauf. Sie belegt keinen byte-identischen Build und wurde nicht als vollständiger End-to-End-Build auf einem frischen Mac verifiziert.

## Voraussetzungen

- Python 3 für `build.sh` und die Plugin-Tests.
- POSIX-`sh`, `tar`, `make` und Standardwerkzeuge aus dem Build-System.
- Zig 0.14.1 für den Smartmontools-Cross-Build.
- Eine vorhandene Zig-Installation; dieses Verfahren installiert oder aktualisiert Zig nicht.

Die offizielle Zig-0.14.1-Dokumentation steht in den [Release Notes](https://ziglang.org/download/0.14.1/release-notes.html). Für heruntergeladene Zig-Archive die Prüfsummen aus dem [offiziellen Download-Index](https://ziglang.org/download/index.json) verwenden. Keine Prüfsummen aus Drittquellen übernehmen.

## Quellenbestand prüfen

Das originale Smartmontools-7.4-Quellarchiv und die Lizenzdateien gehören in:

`src/usr/share/doc/boxsysteminfo/smartmontools/`

Vor dem Build den SHA-256-Wert des Quellarchivs prüfen. Erwartet wird:

`e9a61f641ff96ca95319edfb17948cd297d0cd3342736b2c49c99d4716fb993d`

Alle weiteren Befehle werden im Plugin-Ordner ausgeführt (`cd plugins/BoxSystemInfo` vom Repository-Stamm). Beispiel für ein Archiv mit dem Namen `smartmontools-7.4.tar.gz`:

```sh
sha256sum src/usr/share/doc/boxsysteminfo/smartmontools/smartmontools-7.4.tar.gz
```

Auf macOS kann stattdessen `shasum -a 256` verwendet werden. Den tatsächlichen Dateinamen im Verzeichnis prüfen; keine zusätzliche Archivkopie außerhalb des Plugin-Baums voraussetzen.

## Smartmontools-Binary bauen

Das Skript `tools/build-smartctl.sh` verwendet das Quellarchiv aus dem Plugin-Bestand und Zig 0.14.1. Den absoluten Pfad zum Zig-Programm zur Laufzeit über die Umgebungsvariable `ZIG` angeben, ohne einen Rechnerpfad in Skripten oder Dokumentation fest einzutragen:

```sh
ZIG="$(command -v zig)" ./tools/build-smartctl.sh
```

Vor dem Aufruf sicherstellen, dass `zig` aus `PATH` Version 0.14.1 ist. Das Skript zielt auf `arm-linux-musleabihf` mit `generic+v7a+vfp3d16`. Damit ist keine Kompatibilität mit jeder Enigma2-Box oder jedem Image belegt.

## Plugin-Paket und Tests

Zuerst vom Repository-Stamm in den Plugin-Ordner wechseln. `build.sh` ist ein Shell-Skript; es verwendet intern Python 3:

```sh
./build.sh
```

Beim Paketbau führt `build.sh` außerdem `tools/compile-translations.py` aus. Das Python-3-Skript kompiliert die GNU-gettext-Kataloge (`.po`) zu den mitgelieferten `.mo`-Dateien. Es verwendet nur die Python-Standardbibliothek und benötigt keine zusätzlichen Pakete oder externen Compiler.

Die Tests aus dem Plugin-Stammverzeichnis starten:

```sh
python3 -B -m unittest discover -s tests -v
```

Build-Ausgaben vor dem Commit prüfen. Das Git-Repository soll Quellcode, Skripte, Runtime-Binary, Smartmontools-Quellen und Lizenzen gemeinsam enthalten.

## Verifizierungsgrenzen

OpenPLi und OpenATV sind Ziel-Images; bisher ist nur ein Receiver-/Image-Zielsystem verifiziert. Kein abgeschlossener End-to-End-Build auf einem frischen Mac ist belegt. Aus einem erfolgreichen lokalen Build folgt keine byte-identische Reproduzierbarkeit.

Neue IPKs dürfen erst veröffentlicht werden, wenn der Nutzer genau diese Version selbst auf dem Receiver getestet und ausdrücklich freigegeben hat. Für 0.1.11 liegt diese persönliche Testbestätigung und Veröffentlichungsfreigabe vor. Agenten- oder CI-Tests genügen dafür nicht.

Version 0.1.11 besteht 95 technische Tests und wurde auf dem Receiver sowie durch den Nutzer geprüft. Das veröffentlichte IPK ist das unveränderte getestete Paket; es wird für die Veröffentlichung nicht neu gebaut. Die Änderungen des Zwischenstands 0.1.10 sind enthalten.

## Paketmetadaten

Der Paketbau schreibt neutrale Besitzerangaben (`root`, UID/GID 0), entfernt erweiterte lokale Archivmetadaten und verwendet keine persönlichen Pfade. Das erste öffentliche 0.1.7-Paket wurde so neu verpackt; seine installierbaren Dateien sind bytegleich mit dem bisherigen lokal getesteten Paket.
