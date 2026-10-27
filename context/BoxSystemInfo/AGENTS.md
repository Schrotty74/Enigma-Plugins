# BoxSystemInfo: Arbeitsregeln

Diese Regeln gelten für `plugins/BoxSystemInfo/` und den zugehörigen Kontextordner. Zusätzlich die Regeln im Repository-Stamm beachten.

- Vor Änderungen vollständige relevante Dateien prüfen und neue Vorschläge mit bereits vorhandenen Funktionen abgleichen. Die allgemeine Übersicht bleibt der Startbildschirm; Gelb öffnet Details, Exit führt zurück.
- Aktueller lokaler Teststand: 0.1.10, auf dem Receiver installiert; der Nutzer hat den erfolgreichen Test bestätigt. Die ausdrückliche Veröffentlichungsfreigabe steht noch aus. Letzter öffentlicher und freigegebener Stand: 0.1.9. Das frühere Release 0.1.7 bleibt über seinen Tag erhalten. Neue Arbeiten von einem geprüften Git-Stand aus beginnen und vorhandene Branches prüfen.
- Jede künftig neu veröffentlichte IPK-Version muss zuvor vom Nutzer persönlich getestet und ausdrücklich freigegeben werden. Technische Agenten- oder CI-Tests ersetzen dies nicht.
- Vollständige Quellen, Ressourcen, Build-Skripte, Runtime-Binary, unverändertes smartmontools-Originalquellarchiv und Lizenzen im Plugin-Ordner halten. Neue Rechner müssen mit diesem Bestand und der Bauanleitung weiterarbeiten können. Externe Standardwerkzeuge mit Version und offiziellem Bezug dokumentieren.
- Projektpfade relativ oder zur Laufzeit ermitteln. Keine lokalen Benutzerpfade, privaten Netzadressen, Zugangsdaten, MAC-Adressen, Seriennummern, Receiver-Logs oder Laufzeit-Screenshots veröffentlichen. Vor jedem Upload ausgewählte Git-Dateien und Release-Archive samt Metadaten prüfen.
- Englisch ist der README-Standard (`README.md`), Deutsch liegt in `README.de.md`. Beide gegenseitig verlinken und gemeinsam aktualisieren. Changelog ausschließlich auf Englisch in `CHANGELOG.md`.
- Nach wesentlichen Änderungen und zum Aufgabenende alle vier Kontextdateien aktualisieren. Offene Arbeit in `NEXT_STEPS.md` festhalten; erledigte Punkte nicht als offen stehen lassen.
- Builds nach `plugins/BoxSystemInfo/BUILDING.md`. Keine zusätzlichen Test-Apps oder globalen Umgebungsänderungen ohne Auftrag. Temporäres Material nach Verwendung aufräumen.
- Keine ungeprüfte Kompatibilität oder byte-identische Nachbaubarkeit behaupten. OpenATV und Python 2 sind weiterhin nicht praktisch geprüft.

## README-Aufteilung

Die Repository-Startseite bleibt ein kurzer Plugin-Katalog mit Icon, Kurzbeschreibung und Link. Ausführliche Angaben einschließlich Icon, Funktionen, Bedienung, Installation und Bauanleitung gehören auf die eigenen englischen/deutschen README-Seiten jedes Plugins. Bestehende Detailinformationen bei Sprachänderungen erhalten.
