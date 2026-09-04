# Wasserzähler OCR – Home-Assistant-Add-on

> **Version 1.6.7.** Liest einen Wasserzähler automatisch aus einem
> Kamerabild aus: Bild holen → zuschneiden → Ziffern per OCR erkennen →
> Plausibilität prüfen → Zählerstand und Durchflussrate liefern.
>
> **Alle Einstellungen macht man in der eingebauten Weboberfläche** – die
> Home-Assistant-Add-on-Konfiguration ist bewusst leer.

## Voraussetzungen

- **Home Assistant** mit Add-on-Store (Home Assistant OS oder Supervised).
- Eine **Kamera-Entität**, die ein Standbild des Zählwerks liefert (z. B. eine
  ESP32-CAM per ESPHome). Die Entity-ID trägst du in der Konfiguration ein.
- *Optional* eine **Lampe/LED** als `light.`- oder `switch.`-Entität, die das
  Zählwerk beim Fotografieren ausleuchtet. Die Helligkeit lässt sich einstellen,
  sofern es eine `light.`-Entität mit Helligkeitsunterstützung ist.
- Für die Ziffernerkennung je nach gewähltem Anbieter: nichts weiter
  (Tesseract/TFLite laufen lokal im Add-on), ein erreichbarer **Ollama-Server**
  oder ein **API-Schlüssel** für OpenAI/Gemini/Claude.

## Die Weboberfläche

Alles läuft über den Button **„Benutzeroberfläche öffnen"**. Oben in der
Navigation gibt es fünf Seiten:

- **Übersicht** – Status, letzte Ablesung, Log und „Jetzt auswerten".
- **Konfiguration** – Kamera, Lampe, OCR-Anbieter, Ziffernzahl, KI-Prompt,
  Plausibilität, interne Zugriffsadresse und der „Add-on neu starten"-Button.
- **Bild-Tuner** – Bild holen, drehen, zuschneiden und LED-Helligkeit einstellen.
- **Ziffern** – für TFLite: jede Ziffer als Box im Bild festlegen und die
  Erkennung testen (AI-on-the-edge-Stil).
- **CPU-Auslastung** – Live-Auslastung, vor allem für lokales Ollama nützlich.

## Schnellstart

1. Add-on installieren und starten (siehe unten für den Installationsweg).
2. Auf der Add-on-Seite den Button **„Benutzeroberfläche öffnen"** klicken
   (oder den Eintrag „Wasserzähler" in der Seitenleiste).
3. Auf der Übersichtsseite oben auf **„Konfiguration"** klicken und ausfüllen:
   - **Kamera & Lampe** – welche Home-Assistant-Entitäten das Foto machen.
   - **OCR-Anbieter** – wer die Ziffern liest (siehe unten, „Welchen Anbieter
     wählen?").
   - **Ziffern des Zählwerks** – wie viele schwarze/rote Ziffern dein Zähler hat.
   - **KI-Prompt** *(optional)* – der Text, mit dem die KI zum Ablesen
     aufgefordert wird. Leer lassen für den eingebauten Standard (siehe unten).
   - **LED-Helligkeit** – Helligkeit der Kamera-LED/Lampe in Prozent, einstellbar
     im Bild-Tuner und auf der Ziffern-Seite (0 = ohne Vorgabe). Wird beim
     Bildabruf angewendet – auch im normalen Ablauf.
   - **Plausibilitätsprüfung** – Schutz gegen Fehlablesungen (siehe unten).
   - „Speichern" – wirkt sofort, **kein Add-on-Neustart nötig**.
4. Auf „Übersicht" → **„Bild optimieren (Tuner)"**: Drehwinkel und Zuschnitt
   live einstellen, bis nur noch die Ziffernreihe im Vorschaubild zu sehen
   ist, dann speichern.
5. Zurück zur Übersicht → **„Jetzt auswerten"** klicken. Ergebnis, Bilder und
   eventuelle Fehlermeldungen erscheinen direkt auf der Seite.

Das war's – ab jetzt liest das Add-on regelmäßig automatisch aus (Intervall
stellt man in Home Assistant über den REST-Sensor oder die Integration ein,
siehe unten).

## Wie es aufgebaut ist

```
Home-Assistant-Kamera
        │
        ▼
  Bild holen (+ Lampe kurz an)
        │
        ▼
  Rotieren & Zuschneiden  ←──  im Tuner eingestellt
        │
        ▼
  OCR (Ziffern lesen)     ←──  Anbieter in der Konfiguration gewählt
        │
        ▼
  Plausibilität prüfen    ←──  Schutz gegen Ausreißer
        │
        ▼
  Zählerstand + Durchflussrate + Status
```

Jeder Schritt ist über die Weboberfläche einstellbar, nichts muss in einer
Konfigurationsdatei bearbeitet werden.

## Welchen OCR-Anbieter wählen?

| Anbieter | Kosten | Läuft wo | Erkennungsqualität* |
|---|---|---|---|
| **Tesseract** | kostenlos | im Add-on (lokal) | schwach bei gewölbten Rollenzählwerken, ok bei flachen/gedruckten Anzeigen |
| **TFLite** | kostenlos | im Add-on (lokal, sehr genügsam) | gut bei klar getrennten, gleichmäßig angeordneten Ziffern (Rollenzählwerke) |
| **Ollama – im Add-on** | kostenlos | im Add-on (lokal, braucht RAM) | je nach Modell – siehe RAM-Empfehlung in der Konfiguration |
| **Ollama – eigener Server** | kostenlos | dein eigener Rechner/Server | wie oben, aber ohne den HA-Host zu belasten |
| **OpenAI / Gemini / Claude** | pro Anfrage (Cent-Bereich) | Cloud des Anbieters | am zuverlässigsten in unseren Tests |

*\* Erfahrungswerte aus diesem Projekt mit einem gewölbten NeoVac-Rollenzählwerk.
Bei anderen Zählertypen (flache Digitalanzeige) kann Tesseract deutlich besser
abschneiden.*

**Praktischer Rat:** Starte mit Tesseract, TFLite oder einem kleinen lokalen
Modell zum Testen. Wenn die Erkennung zu oft danebenliegt, wechsle auf Ollama
mit einem stärkeren Modell (die Konfigurationsseite zeigt eine RAM-basierte
Empfehlung) oder auf einen Cloud-Anbieter.

**Bei Cloud-Anbietern:** Es entstehen Kosten pro Anfrage, und das Zählerbild
wird an den jeweiligen Dienst übertragen. Der API-Schlüssel wird lokal auf
diesem Host gespeichert.

**Bei „Ollama – im Add-on":** Ollama wird beim ersten Start mit diesem
Anbieter automatisch heruntergeladen (braucht einmalig Internet) und
persistent in `/data` abgelegt. Die Rechenlast liegt dann auf diesem Host.
Wenn du das lokale Modell wechselst, zuerst „Einstellungen speichern" und dann
den Button **„Add-on neu starten"** (im Bereich des lokalen Ollama) drücken –
erst dann wird das neue Modell geladen.

## TFLite – lokale Ziffernerkennung

Der Anbieter **TFLite** nutzt kleine, lokale Ziffernmodelle im Stil von
„AI-on-the-edge". Jedes Modell erkennt **eine einzelne Ziffer** aus einem
kleinen Bildausschnitt. Zum Lesen des ganzen Zählers wird der (per Bild-Tuner
zugeschnittene) Zahlenausschnitt automatisch in `Hauptziffern + Nachkommaziffern`
**gleich breite Streifen** geteilt und jede Ziffer einzeln klassifiziert. Der
Anbieter ist sehr genügsam (kein Ollama, keine Cloud, CPU-Inferenz im
Millisekunden-Bereich).

Damit das gut funktioniert:
- „Ziffern des Zählwerks" (Haupt-/Nachkommastellen) müssen korrekt eingestellt
  sein – daraus ergibt sich die Zahl der Streifen.
- Im **Bild-Tuner** möglichst eng und gerade auf die Ziffernreihe zuschneiden;
  ungleich breite Ränder verschieben die Streifengrenzen.
- Am besten geeignet für Rollenzählwerke mit klar getrennten, gleichmäßig
  angeordneten Ziffern.

### Modell-Ordner

Die Modelle liegen in einem eigenen Ordner. Auf der **Konfigurationsseite**
(Anbieter „TFLite") werden **alle** gefundenen `.tflite`-Modelle in einer
Auswahlliste angezeigt; „Ordner neu einlesen" aktualisiert die Liste.

Es werden zwei Orte durchsucht (Dateinamen werden dedupliziert):
- `/app/models` – die mitgelieferten Modelle (im Image, schreibgeschützt).
- `/data/models` – **eigene** Modelle; dieser Ordner bleibt über Add-on-Updates
  erhalten. Einfach weitere `.tflite`-Dateien hineinlegen (z. B. per „Studio
  Code Server"- oder „Samba/SSH"-Add-on) und neu einlesen.

Mitgeliefert sind drei Modelle:
- `dig-class11_1910_s2_q.tflite` – 11 Klassen (0–9 plus „unklar"/NaN). Meldet
  eine Ablesung als unklar, wenn eine Ziffer nicht sicher erkannt wird; die
  Ablesung wird dann verworfen statt geraten.
- `dig-class100-0182-s2_q.tflite` – 100 Klassen (0.0–9.9), feinere Auflösung.
- `dig-cont_0900_s3_q.tflite` – kontinuierliches Modell für rollende/analoge
  Ziffern.

Das Add-on erkennt den Modelltyp automatisch an der Ausgabegröße – du musst
also nichts weiter einstellen als die Modellauswahl.

### Ziffern einzeln festlegen (AI-on-the-edge-Stil)

Für die genaueste Erkennung wird **jede Ziffer über eine eigene Box** im Bild
bestimmt, statt den Ausschnitt nur gleichmäßig zu teilen. Öffne dazu die Seite
**„Ziffern"** (Link in der Navigation bzw. Button „Ziffern-Positionen festlegen"
im TFLite-Bereich der Konfiguration):

1. Zuerst im **Bild-Tuner** das Zahlenfeld gerade drehen und grob zuschneiden.
2. Auf der Ziffern-Seite erscheint dieses zugeschnittene Bild. Ziehe für jede
   Ziffer eine Box an ihre Stelle (verschieben in der Mitte, Größe an der blauen
   Ecke). „Gleichmäßig verteilen" legt als Startpunkt so viele Boxen an, wie das
   Zählwerk Ziffern hat. Oben lassen sich außerdem das **TFLite-Modell** wählen
   (gilt auch für den normalen Ablauf) und die **LED-Helligkeit** einstellen –
   „Neues Bild von Kamera holen" lädt ein frisches Bild in dieser Helligkeit.
3. „Positionen speichern".
4. „Erkennung testen" zeigt eine **Übersicht**, was pro Ziffer erkannt wurde –
   mit dem jeweiligen Ausschnitt, der erkannten Ziffer und der Konfidenz – sowie
   die zusammengesetzte Zahl. Genau wie bei AI on the Edge.

Bei jeder normalen Ablesung schneidet das Add-on dann jede Box einzeln aus,
schickt sie durchs Modell und setzt die Ziffern zur Zahl zusammen. Sind keine
Boxen definiert, wird der Ausschnitt ersatzweise gleichmäßig aufgeteilt.

Die Boxen werden als **normierte** Koordinaten (0–1) gespeichert und passen
sich damit unterschiedlichen Bildauflösungen an.

### Genauigkeit verbessern

Wenn ein AI-on-the-edge-Modell schlechte Ergebnisse liefert, helfen diese
Stellschrauben (alle oben auf der Ziffern-Seite):

- **Boxen genau setzen** – „Vereinheitlichen" gibt allen Boxen dieselbe Größe
  und Höhe wie der ausgewählten, danach jede Box anklicken und mit den
  **Pfeiltasten** fein verschieben (mit **Umschalt** Größe ändern). Jede Ziffer
  sollte mittig und gleich im Rahmen sitzen.
- **Eingabe-Normalisierung** umschalten: `0–255` (AI-on-the-edge-Standard) oder
  `0–1` (Werte /255). Je nach Modell liefert die eine oder andere deutlich
  bessere Ergebnisse – im Zweifel beide mit „Erkennung testen" vergleichen.
- **Rollover-Korrektur** (Rollenzählwerk): korrigiert rollende Ziffern anhand
  der Nachbarstelle – eine höhere Ziffer wird erst dann als erhöht gewertet,
  wenn die Stelle rechts davon durch Null gegangen ist (wie bei AI on the Edge).
  Wirkt bei den kontinuierlichen Modellen **dig-cont** und **dig-class100**.
- **Modell wählen**: Für Rollenzählwerke ist **dig-class100** meist die beste
  Wahl (feine Auflösung, robuster Klassifikator), gefolgt von **dig-class11**.
  **dig-cont** ist oft das schwächste der drei – wenn es unzuverlässig ist,
  zuerst dig-class100 probieren.

Die Erkennungs-Übersicht zeigt zu jeder Ziffer den **Rohwert** (z. B. „roh 6.8")
und die Konfidenz – daran erkennst du schnell, ob Boxen, Modell und
Normalisierung passen.

## Installation

### Über den Add-on-Store (empfohlenes Repository)
Siehe die Repository-README, falls du dieses Add-on aus einem Git-Repository
installierst.

### Manuell
1. Diesen Ordner nach `/addons/wasserzaehler_ocr/` auf dem HA-Host kopieren.
2. App-Store neu laden (Einstellungen → Apps → App-Store → drei Punkte →
   neu laden, oder per SSH `ha addons reload`).
3. Unter „Lokale Apps" erscheint „Wasserzähler OCR" → installieren, starten.
4. Weiter mit „Schnellstart" oben.

## Endpunkte (für Fortgeschrittene / die Integration)

| Endpunkt | Zweck |
|---|---|
| `GET /process` | löst eine komplette Ablesung aus, liefert JSON |
| `GET /health` | `{"status": "ok"}` |
| `GET /hostinfo` | interne Container-Adresse (Hostname + `http://<hostname>:5000`) |
| `GET /tflite_models` | Liste der `.tflite`-Modelle im Modell-Ordner |
| `POST /restart_addon` | startet das Add-on neu (z. B. nach Wechsel des lokalen Modells) |
| `GET /digits`, `/digits/base.jpg` | Ziffern-Editor (AI-on-the-edge) und dessen Basisbild |
| `POST /digits/test` | Test-Erkennung mit den Ziffern-Boxen, liefert Übersicht pro Ziffer |
| `GET /status` | Live-Prozessstatus + letztes Ergebnis (für die Übersichtsseite) |
| `GET/POST /settings` | aktuelle Einstellungen lesen/schreiben |
| `GET /system_info` | RAM-Info + Modellempfehlung |
| `GET/POST /set_value` | Zählerstand manuell überschreiben |
| `GET /ollama_status` | Status des aktiven OCR-Anbieters |
| `POST /ollama_delete_unused` | ungenutzte Ollama-Modelle löschen (bis auf das verwendete) |
| `GET /tuner`, `/config`, `/` | die drei Webseiten |

`/process` liefert bei Erfolg zum Beispiel:

```json
{"raw_digits": "01260624", "value": 1260.624, "plausible": true,
 "last_value": 1260.123, "flow_rate_l_min": 0.5, "status": "ok",
 "error_count": 0, "held": false}
```

Felder:
- `value` – Zählerstand in m³. Bleibt bei einer fehlgeschlagenen/unplausiblen
  Ablesung auf dem letzten guten Wert stehen (`held: true`), damit der
  Home-Assistant-Sensor nicht auf „unbekannt" springt.
- `flow_rate_l_min` – Durchflussrate in L/min seit der letzten Messung; `0`
  bei einer fehlgeschlagenen Ablesung, `null` nur beim allerersten Lauf.
- `status` – „ok" oder der Fehlergrund als Text.
- `error_count` – Anzahl aufeinanderfolgender Fehler, `0` nach Erfolg.

## Zählerstand manuell überschreiben

Auf der Übersichtsseite gibt es ein Eingabefeld, vorbefüllt mit dem letzten
ermittelten Wert – nützlich, wenn ein legitimer großer Sprung von der
Plausibilitätsprüfung blockiert wurde. Alternativ per HTTP:
`GET/POST /set_value?value=1265.500`. Der Zeitstempel wird dabei auf jetzt
gesetzt (Durchflussberechnung startet frisch) und der Fehlerzähler
zurückgesetzt.

## Einbindung in Home Assistant

### Zugriffsadresse: nur intern über die Container-Adresse

Die HTTP-API (Port 5000) ist **bewusst nicht ins LAN veröffentlicht** – ein
Zugriff über `http://<HA-HOST-IP>:5000` ist also nicht mehr möglich. Damit ist
die unauthentifizierte API von außen nicht erreichbar.

Aus dem Home-Assistant-Netz heraus (REST-Sensor, Integration) wird das Add-on
stattdessen über seine **interne Container-Adresse** angesprochen – genau wie
bei Frigate (`http://ccab4aaf-frigate:5000`):

`http://<container-hostname>:5000`

Der genaue Hostname wird automatisch ermittelt und auf der
**Konfigurationsseite** unter „Zugriffsadresse für Home Assistant" angezeigt
(mit Kopieren-Button). Die Weboberfläche selbst erreichst du unverändert über
den Button „Benutzeroberfläche öffnen" (Ingress, durch Home Assistant
authentifiziert).

### Über die Custom-Integration (empfohlen)
Siehe das separate Integration-Repository
[watermeter_ocr_integration](https://github.com/geco1986/watermeter_ocr_integration)
(über HACS installierbar) – bindet Zählerstand, Durchfluss, Tagesverbrauch,
Status usw. als native Entitäten ein, inklusive Eingabefeld zur Korrektur direkt
auf der Geräteseite.

### Über REST-Sensoren (Alternative)
```yaml
rest:
  - resource: "http://<container-hostname>:5000/process"   # interne Adresse, siehe Konfigurationsseite
    scan_interval: 120
    timeout: 130
    sensor:
      - name: "Wasserzähler Stand"
        value_template: "{{ value_json.value }}"
        unit_of_measurement: "m³"
        device_class: water
        state_class: total_increasing
      - name: "Wasserzähler Durchfluss"
        value_template: "{{ value_json.flow_rate_l_min }}"
        unit_of_measurement: "L/min"
        state_class: measurement
    binary_sensor:
      - name: "Wasserzähler Status"
        value_template: "{{ value_json.status != 'ok' }}"
        device_class: problem
```

## Speicherort der Daten

Alle Bilder, Einstellungen und Zustandsdateien liegen im privaten
Add-on-Speicher `/data` – nicht im `/config`-Ordner. Sie überstehen
Neustarts und Updates. Die Bilder sind nicht per Samba/File-Editor
erreichbar; ansehen kannst du sie auf der Übersichtsseite.

## Fehlersuche

- Add-on-Log: Einstellungen → Apps → Wasserzähler OCR → Protokoll (zeigt
  auch die letzten Zeilen direkt auf der Übersichtsseite).
- Health-Check (aus dem HA-Netz, z. B. über das „SSH &amp; Web Terminal"-Add-on):
  `curl http://<container-hostname>:5000/health` → `{"status": "ok"}`.
  Aus dem LAN ist die API nicht erreichbar (kein veröffentlichter Host-Port).
- OCR-Anbieter-Status: Konfigurationsseite oder `GET /ollama_status`.
- Ollama erreichbar? `curl http://<OLLAMA-IP>:11434/api/tags`.

## CPU-Auslastung von Ollama begrenzen

Home Assistant bietet für Add-ons keine Möglichkeit, CPU-Kerne oder
-Leistung in der Konfiguration zu begrenzen (das ist eine seit Jahren offene
Anfrage an das Supervisor-Projekt). Das Add-on löst es stattdessen selbst,
über zwei unabhängige Regler in der Konfigurationsseite:

- **CPU-Threads pro Anfrage** (`ollama_num_thread`) – begrenzt, wie viele
  CPU-Threads Ollama für eine einzelne Ablesung verwendet. Wirkt bei
  **beiden** Ollama-Varianten (eingebaut und extern), da der Wert bei jeder
  Anfrage mitgeschickt wird. 0 = Ollama entscheidet automatisch.
- **Maximale CPU-Auslastung** (`ollama_local_cpu_percent`) – eine echte
  Prozent-Drosselung (100% = ein Kern voll ausgelastet, 400% = vier Kerne).
  Wirkt **nur beim eingebauten Ollama** (`ollama_local`), da dafür Zugriff
  auf den laufenden Prozess nötig ist – bei einem externen Server lässt sich
  das von hier aus nicht steuern. 0 = unbegrenzt.

Beide Regler bremsen die Erkennung, wenn sie zu eng gesetzt werden – eine
Ablesung dauert dann länger, dafür bleibt mehr Leistung für Home Assistant
und andere Add-ons übrig. Sinnvoll auf Hosts, die neben diesem Add-on noch
viel anderes laufen lassen.

## CPU-Auslastung aller Kerne

Neue Seite **„CPU-Auslastung"** (über die Navigation oben auf jeder Seite
erreichbar) zeigt:

- Wie viele CPU-Kerne dieser Host hat.
- Die Auslastung **jedes einzelnen Kerns live** (aktualisiert sich jede
  Sekunde) – anders als die Home-Assistant-Systemübersicht, die meist nur
  einen einzelnen Gesamtwert zeigt.
- Zur Einordnung: die aktuell eingestellten CPU-Regler (Threads pro Anfrage,
  maximale Auslastung des eingebauten Ollama).

Nützlich, um direkt zu sehen, ob eine OCR-Anfrage den Host wirklich stark
auslastet und ob die CPU-Regler (siehe oben) etwas bewirken.

## KI-Prompt anpassen

Auf der Konfigurationsseite gibt es die Karte **„KI-Prompt"**: den Text, mit
dem die KI zum Ablesen aufgefordert wird. Das Feld leer zu lassen, verwendet
den eingebauten Standard-Prompt – für die meisten Zähler die beste Wahl. Ein
eigener Prompt ist nützlich, wenn die KI ein besonderes Zählwerk falsch
interpretiert oder eine andere Sprache/Formulierung besser funktioniert.

Der Prompt gilt für die KI-Anbieter **Ollama, OpenAI, Gemini und Claude** –
nicht für Tesseract (klassische OCR ohne Prompt).

Folgende Platzhalter werden vor dem Senden automatisch durch die konkreten
Werte ersetzt:

| Platzhalter | Bedeutung |
|---|---|
| `{main}` | Anzahl der Hauptziffern (schwarz) |
| `{decimal}` | Anzahl der Nachkommaziffern (rot) |
| `{total}` | Gesamtzahl der Ziffern (`main` + `decimal`) |
| `{example}` | Beispiel-Ziffernfolge in passender Länge, z. B. `00000000` |
| `{last_value}` | letzter bekannter Zählerstand (beim allerersten Lauf `unknown`) |

Der **letzte Zählerstand wird der KI als Kontext mitgegeben**: Da der neue Wert
normalerweise gleich oder nur wenig höher ist, kann die KI damit grenzwertige
Ziffern – vor allem die schnell rollenden Nachkommastellen – deutlich besser
bestimmen. Der eingebaute Standard-Prompt enthält dafür bereits einen
Hinweissatz; er wird nur mitgeschickt, wenn schon ein Wert bekannt ist (beim
allerersten Lauf entfällt er). In einem eigenen Prompt kannst du den Wert über
`{last_value}` an beliebiger Stelle einbauen.

Geschweifte Klammern für JSON (z. B. `{ "raw_digits": "…" }`) dürfen frei
verwendet werden und müssen nicht ausmaskiert werden. Der Button
**„Standard-Prompt einsetzen"** füllt das Feld mit der Vorlage zum Anpassen.

> **Wichtig:** Egal wie du den Prompt formulierst – die Antwort der KI muss
> weiterhin ein JSON-Objekt der Form `{ "raw_digits": "…" }` enthalten, sonst
> findet die Auswertung keine Ziffern und die Ablesung schlägt fehl.

## Ungenutzte Ollama-Modelle löschen

In den beiden Ollama-Bereichen der Konfigurationsseite („im Add-on selbst" und
„eigener Server") gibt es je einen Button **„Ungenutzte Modelle löschen"**. Er
listet über die Ollama-API alle heruntergeladenen Modelle auf und entfernt sie
bis auf das aktuell eingetragene – praktisch, um Speicherplatz auf dem
Home-Assistant-Host (bzw. dem externen Ollama-Server) freizugeben, wenn beim
Ausprobieren mehrere Modelle heruntergeladen wurden.

- Vor dem Löschen erscheint eine **Sicherheitsabfrage**, die das zu behaltende
  Modell namentlich nennt. Die Aktion ist unwiderruflich; gelöschte Modelle
  werden bei erneuter Nutzung von Ollama automatisch neu heruntergeladen.
- Geschützt wird das Modell aus dem **Eingabefeld** – auch wenn es noch nicht
  gespeichert wurde, damit die Ausnahme dem entspricht, was du gerade siehst.
- Ist im Feld ein **expliziter Tag** angegeben (z. B. `qwen2.5vl:7b`), wird
  genau dieser geschützt; andere Tags desselben Modells dürfen weg. Ohne Tag
  (z. B. `moondream`) wird über den Basisnamen verglichen, damit auch das
  tatsächlich laufende `moondream:latest` sicher erhalten bleibt.
- Der externe Löschen-Button benötigt eine gültige Server-URL in der
  Konfiguration.
