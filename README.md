# Wasserzähler OCR – Home-Assistant-Add-on-Repository

Dieses Repository enthält das **Wasserzähler-OCR-Add-on**: Es holt das Bild
deiner ESPHome-Kamera, schaltet die Lampe, rotiert/schneidet zu, liest den
Zähler per OCR aus, prüft die Plausibilität und liefert Zählerstand,
Durchflussrate und Status.

Für die Ziffernerkennung stehen mehrere Anbieter zur Wahl: **Tesseract**
(lokal, ohne KI-Modell), **Ollama** (lokal im Add-on oder auf einem eigenen
Server) sowie die Cloud-Dienste **OpenAI**, **Gemini** und **Claude**. Alle
Einstellungen – Kamera, Lampe, OCR-Anbieter, KI-Prompt, Zuschnitt und
Plausibilität – werden komfortabel über die eingebaute Weboberfläche des
Add-ons vorgenommen.

> **Hinweis:** Die zugehörige **Integration** (native HA-Entitäten) liegt in
> einem separaten Repository und wird über HACS installiert. Dieses Repository
> hier ist nur das Add-on.

## Vor dem Hochladen zu GitHub

Ersetze in `repository.yaml` den Platzhalter `DEIN-USER` durch deinen echten
GitHub-Benutzernamen bzw. die echte Repo-URL.

## Installation über den Add-on-Store

1. Dieses Repository zu GitHub hochladen (siehe unten).
2. In Home Assistant: Einstellungen → Add-ons → Add-on-Store → oben rechts die
   drei Punkte → **Repositories** (Repository hinzufügen).
3. Die GitHub-URL dieses Repos einfügen und hinzufügen.
4. Der Store lädt neu; das Add-on „Wasserzähler OCR" erscheint unter
   diesem Repository → installieren.
5. Add-on starten, dann **„Benutzeroberfläche öffnen"** – die gesamte
   Konfiguration (Kamera, Lampe, OCR-Anbieter, Zuschnitt, Plausibilität) läuft
   über die Weboberfläche. Die Add-on-Konfiguration in Home Assistant ist
   bewusst leer.

## Repository zu GitHub hochladen

```bash
cd wasserzaehler_ocr_addon_repo
git init
git add .
git commit -m "Initial commit: Wasserzähler OCR Add-on"
git branch -M main
git remote add origin https://github.com/DEIN-USER/wasserzaehler_ocr_addon.git
git push -u origin main
```

## Inhalt

- `wasserzaehler_ocr/` – das eigentliche Add-on (config.yaml, Dockerfile,
  Python-Module, translations, Icon)
- `wasserzaehler_ocr/pi_setup/` – optionales Skript, falls du Ollama auf einem
  separaten Raspberry Pi betreiben willst

Details zu Konfiguration, Endpunkten und dem `set_value`-Aufruf in
`wasserzaehler_ocr/README.md`.

## Lizenz

MIT – siehe LICENSE.
