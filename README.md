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
> einem separaten Repository und wird über HACS installiert:
> <https://github.com/geco1986/watermeter_ocr_integration>. Dieses Repository
> hier ist nur das Add-on.

## Voraussetzungen

- **Home Assistant** mit Add-on-Store (Home Assistant OS oder Supervised).
- Eine **Kamera-Entität**, die ein Standbild des Zählwerks liefert
  (z. B. ESP32-CAM per ESPHome).
- *Optional* eine **Lampe/LED** (`light.`- oder `switch.`-Entität) zum
  Ausleuchten.
- Für die Ziffernerkennung: nichts weiter (Tesseract/TFLite laufen lokal), oder
  – je nach Wunsch – ein Ollama-Server bzw. ein API-Schlüssel für
  OpenAI/Gemini/Claude.

Ausführliche Details stehen in [`wasserzaehler_ocr/README.md`](wasserzaehler_ocr/README.md).

## Vor dem Hochladen zu GitHub

Dieses Repository ist durchgängig auf den Account **geco1986** und den
Repo-Namen **watermeter_ocr_addon** eingestellt (`repository.yaml`, dieser
Text und der `git`-Befehl unten stimmen überein). Wer es unter einem anderen
Namen veröffentlicht, ersetzt vorher an genau diesen Stellen:

| Platzhalter | Wo | Ersetzen durch |
|---|---|---|
| `geco1986` | `repository.yaml`, `LICENSE`, diese README | deinen GitHub-Account |
| `watermeter_ocr_addon` | `repository.yaml`, diese README | deinen gewünschten Repo-Namen |

> Der **Add-on-Slug** (`wasserzaehler_ocr`, der Ordnername) ist davon
> unabhängig und muss *nicht* geändert werden.

## Installation über den Add-on-Store

1. Dieses Repository zu GitHub hochladen (siehe unten).
2. In Home Assistant: Einstellungen → Add-ons → Add-on-Store → oben rechts die
   drei Punkte → **Repositories** (Repository hinzufügen).
3. Die GitHub-URL dieses Repos einfügen und hinzufügen:
   `https://github.com/geco1986/watermeter_ocr_addon`
4. Der Store lädt neu; das Add-on „Wasserzähler OCR" erscheint unter
   diesem Repository → installieren.
5. Add-on starten, dann **„Benutzeroberfläche öffnen"** – die gesamte
   Konfiguration (Kamera, Lampe, OCR-Anbieter, Zuschnitt, Plausibilität) läuft
   über die Weboberfläche. Die Add-on-Konfiguration in Home Assistant ist
   bewusst leer.

## Repository zu GitHub hochladen

```bash
cd watermeter_ocr_addon      # in den Repo-Ordner wechseln
git init
git add .
git commit -m "Initial commit: Wasserzähler OCR Add-on"
git branch -M main
git remote add origin https://github.com/geco1986/watermeter_ocr_addon.git
git push -u origin main
```

## Inhalt

- `repository.yaml` – macht dieses Repo zu einem Add-on-Store-Repository.
- `wasserzaehler_ocr/` – das eigentliche Add-on (config.yaml, Dockerfile,
  Python-Module, translations, Icon, `CHANGELOG.md`).
- `wasserzaehler_ocr/pi_setup/` – optionales Skript, falls du Ollama auf einem
  separaten Raspberry Pi betreiben willst.
- `.gitignore`, `LICENSE` – Repo-Standarddateien.

Details zu Konfiguration, Endpunkten und dem `set_value`-Aufruf in
`wasserzaehler_ocr/README.md`.

## Lizenz

MIT – siehe LICENSE.
