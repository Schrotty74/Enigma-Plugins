# BoxSystemInfo: Nächste Schritte

0.1.10 ist als lokaler Testbuild implementiert und installiert; 67 technische Tests und Paketbau sind erfolgreich. Die GUI-Prüfung ist erfolgreich: Übersicht und Details, Sprachwahl und Intervallauswahl wurden auf dem Receiver kontrolliert. 0.1.9 bleibt das neueste freigegebene öffentliche IPK.

- Persönlichen Nutzertest von 0.1.10 abwarten: Übersicht, SSD-Fehlerwerte, Netzwerk-Datenrate nach zwei Messungen, aktive DVB-Empfangswerte, Intervallwahl, Deutsch/Englisch.
- 0.1.10-IPK erst nach persönlichem Test und ausdrücklicher Veröffentlichungsfreigabe hochladen. Dann Release-Dokumentation und Kontext von Teststand auf öffentlichen Stand umstellen.

- Git-/Release-Stand `boxsysteminfo-v0.1.9` bei Fortsetzung prüfen; vollständige Quellen, beide READMEs, englischen Changelog und die Kontextdateien zusammen halten.
- OpenATV, weitere Receiver und Python 2 sind noch praktisch ungeprüft. Solche Prüfungen nur bei passendem Auftrag bzw. verfügbarer Zielumgebung durchführen; keine pauschale Kompatibilität behaupten.
- Ein vollständiger Nachbau auf einem frischen Mac und Builds unter einem Checkout-Pfad mit Leerzeichen sind noch nicht nachgewiesen. Bei nächster beauftragter Build-Prüfung berücksichtigen.
- Jede spätere IPK erst nach persönlichem Test und ausdrücklicher Freigabe des Nutzers hochladen. Vor jedem Push und Release-Upload Datenschutzprüfung der konkreten Auswahl ausführen.

Bisherige Releases nicht überschreiben oder löschen. Keine zusätzlichen Funktionen oder breiten Prüfungen ohne Auftrag ergänzen.

## README-Aufteilung

Die Repository-Startseite bleibt ein kurzer Plugin-Katalog mit Icon, Kurzbeschreibung und Link. Ausführliche Angaben einschließlich Icon, Funktionen, Bedienung, Installation und Bauanleitung gehören auf die eigenen englischen/deutschen README-Seiten jedes Plugins. Bestehende Detailinformationen bei Sprachänderungen erhalten.
