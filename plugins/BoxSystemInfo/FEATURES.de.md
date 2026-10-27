# Box Systeminfo — vollständige Funktionsübersicht

[English](FEATURES.md) · [Deutsch](FEATURES.de.md) · [Zurück zur README](README.de.md)

Funktionen des veröffentlichten Releases Box Systeminfo 0.1.11. Hardwareabhängige Werte werden nur angezeigt, wenn Receiver, Laufwerk, Tuner oder Image sie bereitstellen.

## Funktionen

- **Anpassbare Übersicht:** drei gespeicherte Karten aus Temperaturen, RAM, Root-Speicher, Aufnahmespeicher und Netzwerk. Bereits verwendete Karten tauschen ihren Platz.
- **Vier Themes:** Midnight, Ocean, Amber und Light; die Auswahl wird gespeichert.
- **Receiver und Image:** Modell, CPU, Architektur, Laufzeit, Image-Name/-Version, Build/Datum sowie Enigma2-, Kernel- und Python-Version.
- **SSD und SMART:** Temperatur, Modell, Gesamtstatus, Betriebsstunden, unterstützte Fehlerzähler, Reserveplatz und Schreibmengen; Restlebensdauer nur bei eindeutig unterstütztem Prozentattribut.
- **Aufnahmespeicher:** Kapazität, belegter/freier Platz, prozentuale Belegung, Einhängepunkt und Schreibschutzstatus.
- **CPU:** aktive Kerne, aktueller/maximaler Takt und Systemlast über 1/5/15 Minuten.
- **RAM und Swap:** gesamter, verfügbarer, belegter und unbenutzter RAM, bereinigter Cache, Puffer sowie gesamter/belegter/freier Swap.
- **Netzwerk:** Schnittstellentyp, Verbindungsstatus, ausgehandelte Geschwindigkeit sowie Empfangs- und Senderaten in Mbit/s.
- **Aktiver DVB-Tuner:** Signalqualität in dB oder relativem Prozentwert, AGC, BER und Lock sowie erkannte Frontend-Nutzung und Aufnahmezähler.
- **Verlaufskurven:** zehn Minuten Temperatur und Netzwerk-Datenrate, ausschließlich im Sitzungs-RAM; beim Schließen gelöscht.
- **Aktualisierung:** manuell mit OK oder automatisch Aus/2/5/10/30 Sekunden; Standard 5 Sekunden. Automatische SMART-Abfragen höchstens einmal pro Minute.
- **Warnschwellen:** gespeicherte Temperaturgrenzen für SoC/Laufwerk und Belegungsgrenzen für RAM/Speicher sowie Hinweise auf SMART-Fehler und Schreibschutz.
- **Deutsch und Englisch:** Image-Sprache mit englischem Fallback oder direkte Sprachwahl im Menü.
- **Diagnoseexport:** manueller JSON-Bericht nur mit Plugin-Version und ausgewählten Zahlenwerten, Dateimodus 0600 und ohne Upload.
- **Update-Hinweis:** manuelle Suche nach neueren veröffentlichten ARMv7-Paketen; kein automatischer Paketdownload und keine Installation.
- **Vollständiges ARMv7-Paket:** statisches smartctl 7.4, originale smartmontools-Quellen, Lizenzen und Build-Skripte enthalten.

Bedienung, Installation, SMART-Verhalten, Kompatibilität, Diagnose und Build-Anweisungen sind in der [Projekt-README](README.de.md) dokumentiert.
