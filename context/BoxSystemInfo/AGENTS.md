# BoxSystemInfo: Arbeitsregeln

Diese Regeln gelten für `plugins/BoxSystemInfo/` und den zugehörigen Kontextordner. Zusätzlich die Regeln im Repository-Stamm beachten.

- Vor Änderungen vollständige relevante Dateien prüfen und neue Vorschläge mit bereits vorhandenen Funktionen abgleichen. Die allgemeine Übersicht bleibt der Startbildschirm; Gelb öffnet Details, Exit führt zurück.
- Aktueller freigegebener Release-Stand: 0.1.11, Tag `boxsysteminfo-v0.1.11`. Der Nutzer hat das installierte Paket erfolgreich getestet und den IPK-Upload ausdrücklich beauftragt. 0.1.10 war ein Zwischenstand; seine Änderungen sind in 0.1.11 enthalten. Ältere öffentliche Releases bleiben erhalten.
- Jede künftig neu veröffentlichte IPK-Version muss zuvor vom Nutzer persönlich getestet und ausdrücklich freigegeben werden. Technische Agenten- oder CI-Tests ersetzen dies nicht.
- Vollständige Quellen, Ressourcen, Build-Skripte, Runtime-Binary, unverändertes smartmontools-Originalquellarchiv und Lizenzen im Plugin-Ordner halten. Neue Rechner müssen mit diesem Bestand und der Bauanleitung weiterarbeiten können. Externe Standardwerkzeuge mit Version und offiziellem Bezug dokumentieren.
- Projektpfade relativ oder zur Laufzeit ermitteln. Keine lokalen Benutzerpfade, privaten Netzadressen, Zugangsdaten, MAC-Adressen, Seriennummern, Receiver-Logs oder Laufzeit-Screenshots veröffentlichen. Vor jedem Upload ausgewählte Git-Dateien und Release-Archive samt Metadaten prüfen.
- Englisch ist der README-Standard (`README.md`), Deutsch liegt in `README.de.md`. Beide gegenseitig verlinken und gemeinsam aktualisieren. Changelog ausschließlich auf Englisch in `CHANGELOG.md`.
- Nach wesentlichen Änderungen und zum Aufgabenende alle vier Kontextdateien aktualisieren. Offene Arbeit in `NEXT_STEPS.md` festhalten; erledigte Punkte nicht als offen stehen lassen.
- Builds nach `plugins/BoxSystemInfo/BUILDING.md`. Keine zusätzlichen Test-Apps oder globalen Umgebungsänderungen ohne Auftrag. Temporäres Material nach Verwendung aufräumen.
- Keine ungeprüfte Kompatibilität oder byte-identische Nachbaubarkeit behaupten. OpenATV und Python 2 sind weiterhin nicht praktisch geprüft.

## README-Aufteilung

Die Repository-Startseite bleibt ein kurzer Plugin-Katalog mit Icon, Kurzbeschreibung und Link. Ausführliche Angaben einschließlich Icon, Funktionen, Bedienung, Installation und Bauanleitung gehören auf die eigenen englischen/deutschen README-Seiten jedes Plugins. Bestehende Detailinformationen bei Sprachänderungen erhalten.

## Freigegebene Bildergalerie

Der Nutzer hat die Veröffentlichung der zwölf Screenshots von 0.1.11 ausdrücklich beauftragt. Alle Bilder wurden visuell und ihre PNG-Metadaten auf private Daten geprüft. Für diese Aufnahmen gilt eine Ausnahme vom allgemeinen Verbot, Laufzeit-Screenshots zu veröffentlichen. Galerie: `plugins/BoxSystemInfo/GALLERY.md` und `GALLERY.de.md`; Originalbilder unter `docs/screenshots/`. Bei neuen Funktionen nur die betroffenen Seiten neu aufnehmen, neue Seiten ergänzen und unveränderte Bilder behalten. Neue Bilder bis zur Freigabe lokal unter `.local/` bereithalten. Nach persönlichem IPK-Test und ausdrücklichem Upload-Auftrag die geprüften Bilder gemeinsam mit dieser IPK und der aktualisierten Galerie veröffentlichen; keine gesonderte Bildfreigabe für denselben Release verlangen.
