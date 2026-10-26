# Enigma-Plugins

Enigma2-Plugins für ARM-Receiver von Schrotty74. Jedes Plugin besitzt einen eigenen vollständigen Quellcode-Ordner und einen getrennten Arbeitskontext für die Fortsetzung auf einem anderen Rechner.

| Plugin | Beschreibung | Quellcode und Bauanleitung | Arbeitskontext |
|---|---|---|---|
| Box Systeminfo | Übersicht über Temperaturen, RAM, Speicher, Receiver und Image mit vier Themes | [Quellcode](plugins/BoxSystemInfo/) · [Nachbauen](plugins/BoxSystemInfo/BUILDING.md) | [Kontext](context/BoxSystemInfo/PROJECT_CONTEXT.md) · [Chat-Startvorlage](context/BoxSystemInfo/CHAT_TEMPLATE.md) |

## Box Systeminfo

![Box Systeminfo](plugins/BoxSystemInfo/src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/icon.png)

Der stabile Stand auf `main` ist **0.1.7**. Das Plugin zeigt SoC- und Laufwerkstemperatur, Arbeitsspeicher, freien Root-Speicher, Systemlaufzeit und Image-/Build-/Enigma2-Versionen. Midnight, Ocean, Amber und Light sind per Fernbedienung auswählbar. smartctl ist als statisches ARMv7-Programm integriert; es wird kein smartd-Dienst eingerichtet.

Ziel sind offene ARMv7-Enigma2-Images wie OpenPLi und OpenATV. Praktisch geprüft ist OpenPLi auf einer Vu+ Uno 4K SE. Eine allgemeine Kompatibilitätsgarantie besteht nicht.

Installationspakete stehen unter [Releases](https://github.com/Schrotty74/Enigma-Plugins/releases). Der Quellcode-Tag für 0.1.7 heißt `boxsysteminfo-v0.1.7`. Neue IPKs werden erst nach persönlichem Test und ausdrücklicher Freigabe durch den Nutzer veröffentlicht. Die Erweiterungen für 0.1.8 werden getrennt auf `development/boxsysteminfo-0.1.8` erprobt.

## Auf einem neuen Rechner weiterarbeiten

```sh
git clone https://github.com/Schrotty74/Enigma-Plugins.git
cd Enigma-Plugins
```

Dann die [Chat-Startvorlage](context/BoxSystemInfo/CHAT_TEMPLATE.md), den [Projektkontext](context/BoxSystemInfo/PROJECT_CONTEXT.md) und die [Bauanleitung](plugins/BoxSystemInfo/BUILDING.md) lesen. Projektpfade werden aus dem Checkout ermittelt. Receiver-Zugänge werden lokal bereitgestellt und gehören nicht ins Repository.

Der Plugin-Code steht unter der jeweiligen MIT-Lizenz. Für eingebettete Drittprogramme und Laufzeiten gelten die daneben mitgelieferten Lizenztexte; Originalquellen und Build-Skripte sind mitversioniert.
