# BoxSystemInfo: Nächste Schritte

0.1.11 ist implementiert und auf dem Receiver installiert; 95 Tests, Paketbau und Datenschutzprüfung sind erfolgreich. Die GUI-Prüfung ist erfolgreich: Kurven, RAM-Seite, Kartenwechsel, Warnschwellen und Update-Hinweis funktionieren. Englische Verlaufsbeschriftungen wurden geprüft. Ein über die Oberfläche erzeugter Diagnosebericht wurde auf numerische Felder und Modus 0600 geprüft und anschließend gelöscht. 0.1.9 bleibt das neueste öffentliche IPK.

- Persönlichen Nutzertest von 0.1.11 abwarten: Verlauf, Kartenauswahl, Warnschwellen, RAM-Seite, Diagnoseexport und manuelle Update-Prüfung.
- 0.1.11-IPK erst nach persönlichem Test und ausdrücklicher Veröffentlichungsfreigabe hochladen. Dann Release-Dokumentation und Kontext auf den öffentlichen Stand umstellen.
- 0.1.10 wurde vom Nutzer erfolgreich getestet, aber nicht ausdrücklich zur Veröffentlichung freigegeben.

- Git-/Release-Stand `boxsysteminfo-v0.1.9` bei Fortsetzung prüfen; vollständige Quellen, beide READMEs, englischen Changelog und die Kontextdateien zusammen halten.
- OpenATV, weitere Receiver und Python 2 sind noch praktisch ungeprüft. Solche Prüfungen nur bei passendem Auftrag bzw. verfügbarer Zielumgebung durchführen; keine pauschale Kompatibilität behaupten.
- Ein vollständiger Nachbau auf einem frischen Mac und Builds unter einem Checkout-Pfad mit Leerzeichen sind noch nicht nachgewiesen. Bei nächster beauftragter Build-Prüfung berücksichtigen.
- Jede spätere IPK erst nach persönlichem Test und ausdrücklicher Freigabe des Nutzers hochladen. Vor jedem Push und Release-Upload Datenschutzprüfung der konkreten Auswahl ausführen.

Bisherige Releases nicht überschreiben oder löschen. Keine zusätzlichen Funktionen oder breiten Prüfungen ohne Auftrag ergänzen.

## README-Aufteilung

Die Repository-Startseite bleibt ein kurzer Plugin-Katalog mit Icon, Kurzbeschreibung und Link. Ausführliche Angaben einschließlich Icon, Funktionen, Bedienung, Installation und Bauanleitung gehören auf die eigenen englischen/deutschen README-Seiten jedes Plugins. Bestehende Detailinformationen bei Sprachänderungen erhalten.
