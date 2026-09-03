# Änderungsprotokoll

Alle nennenswerten Änderungen an diesem Add-on werden hier festgehalten.
Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/),
die Versionierung an [SemVer](https://semver.org/lang/de/).

## 1.6.5

Erste öffentliche Git-Veröffentlichung – Aufräum- und Verpackungsarbeiten,
keine Funktionsänderung.

### Geändert
- `requirements.txt`: Abhängigkeiten mit Ober-/Untergrenze gepinnt für
  reproduzierbare Builds.
- `Dockerfile`: `io.hass.type` auf den gültigen Wert `addon` korrigiert.
- `repository.yaml` und `LICENSE` auf konsistente Account-/Repo-Angaben gebracht.

### Entfernt
- Ungenutztes Modul `ollama_ocr.py` (wurde nicht ins Image kopiert).

## 1.6.4

Funktionsumfang des Add-ons.

- Automatisches Ablesen des Wasserzählers aus einem Kamerabild:
  Bild holen → rotieren/zuschneiden → OCR → Plausibilitätsprüfung →
  Zählerstand, Durchflussrate und Status.
- OCR-Anbieter zur Auswahl: **Tesseract** und **TFLite** (lokal, ohne Cloud),
  **Ollama** (lokal im Add-on oder auf eigenem Server) sowie die Cloud-Dienste
  **OpenAI**, **Gemini** und **Claude**.
- Eingebaute Weboberfläche (Ingress) für alle Einstellungen: Übersicht,
  Konfiguration, Bild-Tuner, Ziffern-Editor (AI-on-the-edge-Stil) und
  CPU-Auslastung.
- Verbrauchsgrafik für Tag/Woche/Monat/Jahr.
- Interne HTTP-API (Port 5000) für REST-Sensor und die separate Integration;
  bewusst nicht ins LAN veröffentlicht.
