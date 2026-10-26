# BoxSystemInfo: Nächste Schritte

## Ausgangspunkt

Der stabile 0.1.7-Stand ist aus Paket und vollständigem Quellenbestand übernommen. Datenschutzprüfung und bytegleicher Vergleich der installierbaren Dateien sind abgeschlossen. Quellcode, Tag `boxsysteminfo-v0.1.7` und bereinigtes IPK sind veröffentlicht. Keine 0.1.7-Dateien durch den geplanten 0.1.8-Stand ersetzen.

## Entwicklung 0.1.8

Nach Übernahme des Ausgangsstands die sechs vorgesehenen Änderungen ausschließlich auf `development/boxsysteminfo-0.1.8` umsetzen. Build- und Testskripte müssen die Originalquellen und Lizenzdateien aus dem Plugin-Verzeichnis verwenden und ohne persönliche Pfade laufen.

Vor einer Freigabe:

1. Geänderte Quelltexte und Kontextdokumente vollständig prüfen.
2. Die vorhandenen Plugin-Tests ausführen: `python3 -B -m unittest discover -s tests -v`.
3. Build-Artefakte und ihre Herkunft dokumentieren; keine byte-identische Reproduzierbarkeit behaupten.
4. Nutzer muss 0.1.8 selbst auf dem Receiver testen und ausdrücklich freigeben.

## Veröffentlichungssperre

Bis zur persönlichen Nutzerprüfung und ausdrücklichen Zustimmung keine 0.1.8-IPK auf eine öffentliche Release-Seite hochladen oder anderweitig veröffentlichen. Automatisierte oder Agententests sind keine Freigabe.
