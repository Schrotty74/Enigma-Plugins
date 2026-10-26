# Mitgeliefertes smartctl 7.4

Dieses Paket enthält einen eigenen statischen ARMv7-Linux-Build von smartctl 7.4, ausschließlich zum Lesen vorhandener Temperaturdaten. smartd und Update-Skripte werden nicht mitinstalliert. Der Plugin-Code steht unter MIT; für smartctl gilt GPL Version 2. Die jeweiligen Laufzeitlizenzen liegen daneben.

## Quelle und Übersetzung

- Originalquellcode: [smartmontools 7.4](https://downloads.sourceforge.net/smartmontools/smartmontools-7.4.tar.gz), unverändert als `smartmontools-7.4.tar.gz` mitgeliefert.
- SHA256 des Quellarchivs: `e9a61f641ff96ca95319edfb17948cd297d0cd3342736b2c49c99d4716fb993d`.
- Compiler: [Zig 0.14.1](https://ziglang.org/download/0.14.1/release-notes.html), C/C++-Treiber mit musl und libc++.
- Ziel: `arm-linux-musleabihf`, CPU `generic+v7a+vfp3d16`, Optimierung `-Os -g0`, Linker `-static -s`.
- Configure: `--build=aarch64-apple-darwin --host=arm-linux-musleabihf --without-libcap-ng --without-selinux --without-libsystemd --with-update-smart-drivedb=no`.
- `SOURCE_DATE_EPOCH=1690887634` unterdrückt lokale Build-Pfade in der Versionsausgabe.
- Build-Skript: `tools/build-smartctl.sh` im vollständigen Quellcode-ZIP. Es verwendet den mitgelieferten Originalquellcode ohne Patches und baut nur das Ziel `smartctl`.
- SHA256 des ausgelieferten Programms: `e40a3be0cfdef14405ad2d6d7e50b725801bc0d7b2d2fcd1ca56b140901e7337`.

Der frühere Diagnose-Aufruf verwendete die Datei aus dem offiziellen OpenPLi-Paket `smartmontools_7.4-r0.12_armv7ahf-neon.ipk`. Diese dynamisch gelinkte Datei ist nicht die im Plugin ausgelieferte Datei. Der eigene statische Build soll die Bindung an Systembibliotheken dieses Images vermeiden. Eine Prüfung auf OpenATV oder weiteren Receivern steht aus.

## Aktualisierung

smartctl wird zusammen mit dem Plugin installiert und entfernt. Ein neues Plugin-Paket kann eine neuere geprüfte smartctl-Version enthalten. Es gibt keinen eigenen Download- oder Update-Dienst. Eine unabhängig vom Plugin installierte smartmontools-Version wird nicht verändert.
