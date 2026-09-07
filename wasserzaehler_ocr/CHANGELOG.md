# Änderungsprotokoll

Alle nennenswerten Änderungen an diesem Add-on werden hier festgehalten.
Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/),
die Versionierung an [SemVer](https://semver.org/lang/de/).

## 1.7.1

### Hinzugefügt
- **Zählertyp Gas.** Zusätzlich zu Wasser/Strom/Wärme wählbar; Zählerstand in
  m³, Momentanwert als Durchfluss in m³/h. Eigene Badge-Farbe in der
  Zähler-Verwaltung.
  > Hinweis: Damit ein Gaszähler in Home Assistant auch als Gas-Gerät
  > erscheint, muss die zugehörige Integration den Typ `gas` kennen
  > (ab Integrations-Version mit Gas-Unterstützung). Ältere Integrationen
  > behandeln unbekannte Typen als Wasser.

### Behoben
- **Layout der Zähler-Verwaltung überarbeitet.** Auswählen, Umbenennen und
  Neu-Anlegen sind klar getrennt: aktive Anzeige als Banner, anklickbare
  Zähler-Zeilen mit Typ-Badge, Umbenennen/Typ ändern per Stift, Löschen per
  Papierkorb. Behebt Überlappungen und die doppelte Typ-Auswahl.
- **Zähler-Umschalter in der Kopfzeile** ist nicht mehr überbreit.

## 1.7.0

### Hinzugefügt
- **Mehrere Zähler / Kameras.** Das Add-on kann jetzt beliebig viele Zähler
  verwalten – jeder mit eigener Kamera, Lampe, eigenem Bildzuschnitt, eigenen
  Ziffern-Boxen, eigenem OCR-Anbieter samt Prompt und Zugangsdaten sowie
  eigenem gespeicherten Stand und Verlauf. Verwaltung (anlegen, umbenennen,
  Typ ändern, löschen) direkt auf der Konfigurationsseite; oben in der Leiste
  wählt man den aktiven Zähler.
- **Zählertypen Wasser / Strom / Wärme.** Pro Zähler wählbar; die Übersicht
  zeigt passende Einheiten (m³ bzw. kWh, Momentanwert als Durchfluss in L/min,
  Leistung in W bzw. kW).
- **Discovery-Endpunkt `GET /meters`** liefert die Zählerliste (`id`, `name`,
  `type`) für die Integration ab v1.7.0.
- **Neue Verwaltungs-Endpunkte** `POST /meters`, `POST /meter_update`,
  `POST /meter_delete`, `POST /meter_active`.

### Geändert
- **`GET /process` akzeptiert `?id=<zähler>`** und liefert zusätzlich `id`,
  `type` und einen typgerechten Momentanwert `rate` (Wasser weiterhin auch
  `flow_rate_l_min`). Ohne `id` gilt der aktive Zähler (Rückwärtskompatibilität).
- **`POST /set_value` akzeptiert `{id, value}`** und setzt den Stand des
  jeweiligen Zählers.
- **`/status`, `/settings`, `/tuner/*`, `/digits/*`, `/ollama_status`,
  `/chart_data`** beziehen sich auf den gewählten Zähler (`?id`).
- Zustand, Verlauf, Tuning und Bilder werden pro Zähler getrennt gespeichert
  (`state_<id>.json`, `history_<id>.json`, `tuning_<id>.json`, `img_<id>_*.jpg`).

### Migration
- Ein bestehendes Einzel-Setup wird beim ersten Start automatisch als Zähler
  „zaehler1" (Typ Wasser) übernommen – inklusive gespeichertem Stand, Verlauf
  und Zuschnitt. Es geht nichts verloren.

## 1.6.7

### Geändert
- **Material-Design-Überarbeitung der gesamten Weboberfläche.** Neues,
  self-contained Design-System (`app.css`) mit Material-angelehnten Karten,
  Buttons, Formularfeldern, Elevation und Hell-/Dunkel-Modus. Keine externen
  Schriften oder CDNs – funktioniert vollständig offline.
- **Icons überall.** Inline-SVG-Icon-Sprite (`app.js`) für Navigation,
  Kartenüberschriften und Schaltflächen.
- **Mehrsprachigkeit (Deutsch/Englisch).** Automatische Erkennung der
  Browsersprache plus sichtbarer DE/EN-Umschalter in der App-Bar; zentrale
  i18n-Engine in `app.js`. Übersicht, Einrichtung und Info sind vollständig
  zweisprachig; auf den übrigen Seiten sind Navigation, Titel, Kartentitel
  und Schaltflächen übersetzt.
- **Gemeinsame App-Bar mit Tab-Navigation** auf allen Seiten (statt pro Seite
  wiederholtem Kopf/Menü).

### Hinzugefügt
- **Neue Seite „Einrichtung"** – Schritt-für-Schritt-Anleitung von der Kamera
  bis zur Einbindung in Home Assistant.
- **Neue Seite „Info & System"** – Add-on-Version, aktiver OCR-Anbieter und
  dessen Status, CPU/RAM, interne Zugriffsadresse und Diagnose auf einen Blick.
- `/health` liefert jetzt zusätzlich die Add-on-Version; neue Routen
  `/app.js`, `/help`, `/info`.


Modernisierte Weboberfläche – reine Design-Änderung, keine Funktionsänderung.

### Geändert
- Gemeinsames Design-System als `app.css` (über die Route `/app.css`
  ausgeliefert) statt fünffach dupliziertem CSS pro Seite.
- **Automatischer Hell-/Dunkel-Modus** je nach Systemeinstellung
  (`prefers-color-scheme`) über CSS-Tokens.
- Einheitlicher Kopfbereich und Pill-Navigation auf allen Seiten
  (Übersicht, Konfiguration, Bild-Tuner, Ziffern, CPU-Auslastung); zuvor
  teils inline-gestylte, uneinheitliche Navigation.
- Fokus-Ringe für Tastaturbedienung, weichere Karten mit dezenten Schatten,
  konsistente Buttons/Formulare, Rücksicht auf „Bewegung reduzieren".

Alle Element-IDs und CSS-Klassen blieben unverändert – die Bedienung und die
JavaScript-Logik der Seiten sind identisch.

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
