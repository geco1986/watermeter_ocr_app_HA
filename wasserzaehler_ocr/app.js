/* ==========================================================================
   Wasserzähler OCR – gemeinsame Front-End-Logik (self-contained).
   - Inline-SVG-Icon-Sprite (keine externen Icon-Fonts/CDNs)
   - Mehrsprachigkeit DE/EN: Auto-Erkennung + sichtbarer Umschalter
   - gemeinsame Material-App-Bar mit Tab-Navigation
   - Ripple-Effekt für Buttons
   Wird über /app.js als blockierendes <script> im <head> geladen, damit
   t() den seiten-eigenen Skripten am Seitenende bereits zur Verfügung steht.
   ========================================================================== */
(function () {
  "use strict";

  /* ---------------- Icon-Sprite (24x24, fill=currentColor) ---------------- */
  var ICONS = {
    drop: "M12 2.6C8.4 6.3 5.5 10 5.5 13.5A6.5 6.5 0 0012 20a6.5 6.5 0 006.5-6.5C18.5 10 15.6 6.3 12 2.6z",
    dashboard: "M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z",
    tune: "M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z",
    crop: "M17 15h2V7c0-1.1-.9-2-2-2H9v2h8v8zM7 17V1H5v4H1v2h4v10c0 1.1.9 2 2 2h10v4h2v-4h4v-2H7z",
    grid: "M4 8h4V4H4v4zm6 12h4v-4h-4v4zm-6 0h4v-4H4v4zm0-6h4v-4H4v4zm6 0h4v-4h-4v4zm6-10v4h4V4h-4zm-6 4h4V4h-4v4zm6 6h4v-4h-4v4zm0 6h4v-4h-4v4z",
    memory: "M15 9H9v6h6V9zm4 2V9h2V7h-2V5c0-1.1-.9-2-2-2h-2V1h-2v2h-2V1H9v2H7c-1.1 0-2 .9-2 2v2H3v2h2v2H3v2h2v2c0 1.1.9 2 2 2h2v2h2v-2h2v2h2v-2h2c1.1 0 2-.9 2-2v-2h2v-2h-2v-2h2zm-4 6H7V7h10v10z",
    help: "M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z",
    info: "M11 7h2v2h-2V7zm0 4h2v6h-2v-6zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z",
    play: "M8 5v14l11-7z",
    save: "M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z",
    refresh: "M17.65 6.35A7.96 7.96 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z",
    edit: "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a.996.996 0 000-1.41l-2.34-2.34a.996.996 0 00-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z",
    check: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z",
    alert: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z",
    translate: "M12.87 15.07l-2.54-2.51.03-.03A17.5 17.5 0 0014.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z",
    camera: "M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15a5 5 0 110-10 5 5 0 010 10zm0-2a3 3 0 100-6 3 3 0 000 6z",
    bolt: "M11 21h-1l1-7H7.5c-.58 0-.57-.32-.38-.66.19-.34.05-.08.07-.12C8.48 10.94 10.42 7.54 13 3h1l-1 7h3.5c.49 0 .56.33.47.51l-.07.15C12.96 17.55 11 21 11 21z",
    delete: "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z",
    image: "M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z",
    link: "M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7a5 5 0 000 10h4v-1.9H7A3.1 3.1 0 013.9 12zM8 13h8v-2H8v2zm9-6h-4v1.9h4a3.1 3.1 0 010 6.2h-4V17h4a5 5 0 000-10z",
    terminal: "M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8h16v10zM6 10.5l1-1L9.5 12 7 14.5l-1-1L7.5 12 6 10.5zM11 14h5v-1h-5v1z",
    cloud: "M19.35 10.04A7.49 7.49 0 0012 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 000 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z",
    clock: "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z",
    gauge: "M12 4C7 4 3 8 3 13c0 2 .6 3.8 1.7 5.3l1.5-1.2A6.94 6.94 0 015 13a7 7 0 0114 0c0 1.6-.5 3-1.4 4.1l1.5 1.2A8.94 8.94 0 0021 13c0-5-4-9-9-9zm-1 4v5a2 2 0 102 0V8h-2z",
    ram: "M20 6H4c-1.1 0-2 .9-2 2v6h3v3h2v-3h2v3h2v-3h2v3h2v-3h3V8c0-1.1-.9-2-2-2zM8 12H6v-2h2v2zm5 0h-2v-2h2v2zm5 0h-2v-2h2v2z",
    droplet: "M12 2.6C8.4 6.3 5.5 10 5.5 13.5A6.5 6.5 0 0012 20a6.5 6.5 0 006.5-6.5C18.5 10 15.6 6.3 12 2.6z",
    router: "M11 15h2v3h-2zM6 15h2v3H6zm10 0h2v3h-2zM19 8h-2.81a5.99 5.99 0 00-1.82-1.96L16 3.36 14.24 2.4 12 6.6 9.76 2.4 8 3.36l1.63 2.68A5.99 5.99 0 007.81 8H5c-1.1 0-2 .9-2 2v2c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-2c0-1.1-.9-2-2-2z",
    copy: "M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"
  };

  function buildSprite() {
    var s = '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">';
    for (var k in ICONS) {
      s += '<symbol id="ic-' + k + '" viewBox="0 0 24 24"><path d="' + ICONS[k] + '"/></symbol>';
    }
    return s + "</svg>";
  }
  function icon(name, cls) {
    return '<svg class="icon' + (cls ? " " + cls : "") + '" aria-hidden="true"><use href="#ic-' + name + '"></use></svg>';
  }

  /* ------------------------------ i18n ------------------------------------ */
  var I18N = {
    de: {
      "nav.overview": "Übersicht", "nav.config": "Konfiguration", "nav.tuner": "Bild-Tuner",
      "nav.digits": "Ziffern", "nav.cpu": "CPU", "nav.help": "Einrichtung", "nav.info": "Info",
      "brand.sub": "Wasserzähler OCR",

      "common.run": "Jetzt auswerten", "common.save": "Speichern", "common.reset": "Zurücksetzen",
      "common.refresh": "Aktualisieren", "common.check": "Prüfen", "common.saving": "Speichere…",
      "common.saved": "Gespeichert", "common.loading": "Lade…", "common.none": "–",
      "common.never": "noch nie", "common.yes": "ja", "common.no": "nein", "common.unit_m3": "m³",

      "phase.idle": "bereit", "phase.fetch": "Bild holen", "phase.rotate": "Zuschneiden",
      "phase.ocr": "OCR läuft", "phase.plausibility": "Plausibilität", "phase.done": "fertig",
      "phase.error": "Fehler", "phase.running": "läuft: ",

      "prov.ollama_local": "Ollama (im Add-on)", "prov.ollama_remote": "Ollama (extern)",
      "prov.openai": "OpenAI", "prov.gemini": "Gemini", "prov.claude": "Claude",
      "prov.tesseract": "Tesseract", "prov.tflite": "TFLite",

      "idx.title": "Übersicht", "idx.sub": "Aktueller Stand, Steuerung und letzte Auswertung.",
      "idx.current": "Aktueller Stand", "idx.value": "Zählerstand", "idx.flow": "Durchfluss",
      "idx.lastRead": "Zuletzt erfolgreich gelesen", "idx.errCount": "Fehlerzähler",
      "idx.tunerBtn": "Bild optimieren", "idx.lastResult": "Letztes Ergebnis",
      "idx.noResult": "Noch keine Auswertung in dieser Sitzung.",
      "idx.override": "Zählerstand überschreiben",
      "idx.overrideDesc": "Vorbefüllt mit dem letzten Wert. Anpassen und speichern, z. B. nach einem blockierten großen Sprung.",
      "idx.fillLast": "Letzten Wert einsetzen", "idx.images": "Bilder der letzten Analyse",
      "idx.dstCap": "an die OCR gesendet (zugeschnitten)", "idx.srcCap": "Rohbild der Kamera",
      "idx.refreshImg": "Bilder aktualisieren", "idx.provider": "OCR-Anbieter",
      "idx.connection": "Verbindung", "idx.model": "Modell", "idx.modelPresent": "Modell vorhanden",
      "idx.logs": "Letzte Protokollzeilen", "idx.raw": "Rohwert", "idx.status": "Status",
      "idx.plausible": "Plausibel", "idx.hint": "Hinweis", "idx.held": "letzter Wert gehalten",
      "idx.compare": "Vergleichswert", "idx.errDetails": "Fehlerdetails:",
      "idx.enterNumber": "Bitte eine Zahl eingeben.", "idx.savedValue": "Gespeichert: ",
      "idx.reachable": "erreichbar", "idx.unreachable": "nicht erreichbar",
      "idx.allReady": "Alles bereit.", "idx.connectedNoModel": "Verbunden, aber Modell nicht gefunden.",
      "idx.notReachable": "Nicht erreichbar: ",

      "info.title": "Info & System", "info.sub": "Versionen, Anbieterstatus und Diagnose auf einen Blick.",
      "info.versions": "Version & Anbieter", "info.addonVersion": "Add-on-Version",
      "info.activeProvider": "Aktiver OCR-Anbieter", "info.providerStatus": "Anbieter-Status",
      "info.system": "System", "info.cpuCores": "CPU-Kerne", "info.cpuLoad": "CPU-Auslastung",
      "info.ram": "Arbeitsspeicher (frei/gesamt)", "info.connectivity": "Anbindung",
      "info.internalUrl": "Interne Adresse (REST/Integration)",
      "info.internalHint": "Diese Adresse trägst du im REST-Sensor bzw. in der Integration ein.",
      "info.diag": "Diagnose", "info.rerun": "Werte neu abrufen",
      "info.diagHint": "Die Integration wird separat über HACS installiert und liest genau diese Werte aus.",

      "help.title": "Einrichtung", "help.sub": "In wenigen Schritten vom Kamerabild zum Zählerstand.",
      "help.introTitle": "So funktioniert es",
      "help.intro": "Eine Kamera (z. B. ESP32-CAM) macht nur ein Foto vom Zählwerk. Das Add-on dreht und schneidet das Bild zu, liest die Ziffern per OCR und prüft das Ergebnis auf Plausibilität. Die Werte holt sich Home Assistant über die separate Integration oder einen REST-Sensor.",
      "help.s1": "Kamera bereitstellen",
      "help.s1d": "Richte eine Kamera-Entität in Home Assistant ein, die das Zählwerk zeigt (z. B. ESP32-CAM). Optional eine Lampe/LED für gleichmäßiges Licht. Beides trägst du in der Konfiguration ein.",
      "help.s2": "Add-on konfigurieren",
      "help.s2d": "Öffne die Konfiguration und wähle Kamera, optional die Lampe und den OCR-Anbieter (Tesseract oder TFLite laufen lokal ohne Cloud). Änderungen wirken sofort.",
      "help.s3": "Bild ausrichten (Tuner)",
      "help.s3d": "Im Bild-Tuner drehst und beschneidest du das Kamerabild so, dass nur das Zählwerk sichtbar ist. Live-Vorschau prüfen, dann speichern.",
      "help.s4": "Ziffern festlegen",
      "help.s4d": "Nur für TFLite: Markiere auf der Ziffern-Seite jede Ziffernstelle mit einer Box und teste die Erkennung. Für Tesseract/Ollama/Cloud nicht nötig.",
      "help.s5": "Erste Auswertung",
      "help.s5d": "Zurück auf der Übersicht auf „Jetzt auswerten“ klicken. Der Zählerstand, die Bilder und das Protokoll erscheinen sofort.",
      "help.s6": "In Home Assistant einbinden",
      "help.s6d": "Installiere die Integration „Wasserzähler OCR“ über HACS und trage die interne Adresse aus der Info-Seite ein – oder nutze einen REST-Sensor. Danach stehen Zählerstand, Durchfluss und Tagesverbrauch als Entitäten bereit.",
      "help.openPage": "Seite öffnen",

      "cfg.title": "Konfiguration", "cfg.sub": "Alle Einstellungen – wirken sofort, kein Neustart nötig",
      "cfg.addr": "Zugriffsadresse für Home Assistant", "cfg.cam": "Kamera & Lampe",
      "cfg.provider": "OCR-Anbieter", "cfg.mem": "Systemspeicher & Modellempfehlung",
      "cfg.digits": "Ziffern des Zählwerks", "cfg.prompt": "KI-Prompt",
      "cfg.plaus": "Plausibilitätsprüfung",
      "tun.title": "Bild-Tuner", "tun.sub": "Rotation & Zuschnitt live einstellen, Vorschau prüfen, dann speichern.",
      "tun.source": "Quellbild", "tun.settings": "Einstellungen", "tun.preview": "Vorschau (Ergebnis)",
      "dig.title": "Ziffern festlegen", "dig.sub": "AI on the Edge – jede Ziffer als Box festlegen und die Erkennung testen",
      "dig.imgModel": "Bild & Modell", "dig.positions": "Ziffern-Positionen", "dig.test": "Erkennung testen",
      "cpu.title": "CPU-Auslastung", "cpu.sub": "Alle Kerne einzeln, live – Home Assistant zeigt sonst nur einen Gesamtwert",
      "cpu.host": "Dieser Host", "cpu.perCore": "Auslastung je Kern", "cpu.regulators": "Aktuelle CPU-Regler",
      "btn.copy": "Kopieren", "btn.rescan": "Ordner neu einlesen", "btn.delUnused": "Ungenutzte Modelle löschen",
      "btn.restart": "Add-on neu starten", "btn.defaultPrompt": "Standard-Prompt einsetzen",
      "btn.reload": "Neu laden", "btn.apply": "übernehmen", "btn.fetchImg": "Neues Bild von Kamera holen",
      "btn.saveOverride": "Werte speichern (überschreiben)", "btn.resetConfig": "Auf Add-on-Konfig zurücksetzen",
      "btn.distribute": "Gleichmäßig verteilen", "btn.unify": "Vereinheitlichen",
      "btn.digitPlus": "Ziffer +", "btn.digitMinus": "Ziffer −", "btn.reloadImg": "Bild neu laden",
      "btn.savePos": "Positionen speichern", "btn.testRec": "Erkennung testen"
    },
    en: {
      "nav.overview": "Overview", "nav.config": "Configuration", "nav.tuner": "Image tuner",
      "nav.digits": "Digits", "nav.cpu": "CPU", "nav.help": "Setup", "nav.info": "Info",
      "brand.sub": "Water Meter OCR",

      "common.run": "Run now", "common.save": "Save", "common.reset": "Reset",
      "common.refresh": "Refresh", "common.check": "Check", "common.saving": "Saving…",
      "common.saved": "Saved", "common.loading": "Loading…", "common.none": "–",
      "common.never": "never", "common.yes": "yes", "common.no": "no", "common.unit_m3": "m³",

      "phase.idle": "ready", "phase.fetch": "fetching image", "phase.rotate": "cropping",
      "phase.ocr": "OCR running", "phase.plausibility": "plausibility", "phase.done": "done",
      "phase.error": "error", "phase.running": "running: ",

      "prov.ollama_local": "Ollama (in add-on)", "prov.ollama_remote": "Ollama (external)",
      "prov.openai": "OpenAI", "prov.gemini": "Gemini", "prov.claude": "Claude",
      "prov.tesseract": "Tesseract", "prov.tflite": "TFLite",

      "idx.title": "Overview", "idx.sub": "Current reading, controls and the latest result.",
      "idx.current": "Current reading", "idx.value": "Meter reading", "idx.flow": "Flow rate",
      "idx.lastRead": "Last successful read", "idx.errCount": "Error counter",
      "idx.tunerBtn": "Optimise image", "idx.lastResult": "Latest result",
      "idx.noResult": "No analysis yet in this session.",
      "idx.override": "Override meter reading",
      "idx.overrideDesc": "Pre-filled with the last value. Adjust and save, e.g. after a blocked large jump.",
      "idx.fillLast": "Insert last value", "idx.images": "Images of the last analysis",
      "idx.dstCap": "sent to OCR (cropped)", "idx.srcCap": "raw camera image",
      "idx.refreshImg": "Refresh images", "idx.provider": "OCR provider",
      "idx.connection": "Connection", "idx.model": "Model", "idx.modelPresent": "Model present",
      "idx.logs": "Recent log lines", "idx.raw": "Raw value", "idx.status": "Status",
      "idx.plausible": "Plausible", "idx.hint": "Note", "idx.held": "kept last value",
      "idx.compare": "Comparison value", "idx.errDetails": "Error details:",
      "idx.enterNumber": "Please enter a number.", "idx.savedValue": "Saved: ",
      "idx.reachable": "reachable", "idx.unreachable": "not reachable",
      "idx.allReady": "All set.", "idx.connectedNoModel": "Connected, but model not found.",
      "idx.notReachable": "Not reachable: ",

      "info.title": "Info & system", "info.sub": "Versions, provider status and diagnostics at a glance.",
      "info.versions": "Version & provider", "info.addonVersion": "Add-on version",
      "info.activeProvider": "Active OCR provider", "info.providerStatus": "Provider status",
      "info.system": "System", "info.cpuCores": "CPU cores", "info.cpuLoad": "CPU load",
      "info.ram": "Memory (free/total)", "info.connectivity": "Connectivity",
      "info.internalUrl": "Internal address (REST/integration)",
      "info.internalHint": "Enter this address in the REST sensor or the integration.",
      "info.diag": "Diagnostics", "info.rerun": "Fetch values again",
      "info.diagHint": "The integration is installed separately via HACS and reads exactly these values.",

      "help.title": "Setup", "help.sub": "From camera image to meter reading in a few steps.",
      "help.introTitle": "How it works",
      "help.intro": "A camera (e.g. ESP32-CAM) only takes a photo of the counter. The add-on rotates and crops the image, reads the digits via OCR and checks the result for plausibility. Home Assistant fetches the values via the separate integration or a REST sensor.",
      "help.s1": "Provide a camera",
      "help.s1d": "Set up a camera entity in Home Assistant that shows the counter (e.g. ESP32-CAM). Optionally a lamp/LED for even lighting. You enter both in the configuration.",
      "help.s2": "Configure the add-on",
      "help.s2d": "Open the configuration and pick the camera, optionally the lamp, and the OCR provider (Tesseract or TFLite run locally without any cloud). Changes take effect immediately.",
      "help.s3": "Align the image (tuner)",
      "help.s3d": "In the image tuner, rotate and crop the camera image so only the counter is visible. Check the live preview, then save.",
      "help.s4": "Define the digits",
      "help.s4d": "Only for TFLite: on the Digits page, mark each digit position with a box and test the recognition. Not needed for Tesseract/Ollama/cloud.",
      "help.s5": "First analysis",
      "help.s5d": "Back on the overview, click “Run now”. The reading, the images and the log appear right away.",
      "help.s6": "Integrate into Home Assistant",
      "help.s6d": "Install the “Water Meter OCR” integration via HACS and enter the internal address from the Info page – or use a REST sensor. Reading, flow rate and daily consumption then appear as entities.",
      "help.openPage": "Open page",

      "cfg.title": "Configuration", "cfg.sub": "All settings – take effect immediately, no restart needed",
      "cfg.addr": "Address for Home Assistant", "cfg.cam": "Camera & lamp",
      "cfg.provider": "OCR provider", "cfg.mem": "System memory & model recommendation",
      "cfg.digits": "Counter digits", "cfg.prompt": "AI prompt",
      "cfg.plaus": "Plausibility check",
      "tun.title": "Image tuner", "tun.sub": "Adjust rotation & crop live, check the preview, then save.",
      "tun.source": "Source image", "tun.settings": "Settings", "tun.preview": "Preview (result)",
      "dig.title": "Define digits", "dig.sub": "AI on the Edge – mark each digit as a box and test recognition",
      "dig.imgModel": "Image & model", "dig.positions": "Digit positions", "dig.test": "Test recognition",
      "cpu.title": "CPU load", "cpu.sub": "Every core individually, live – Home Assistant otherwise shows only a single total",
      "cpu.host": "This host", "cpu.perCore": "Load per core", "cpu.regulators": "Current CPU limits",
      "btn.copy": "Copy", "btn.rescan": "Rescan folder", "btn.delUnused": "Delete unused models",
      "btn.restart": "Restart add-on", "btn.defaultPrompt": "Insert default prompt",
      "btn.reload": "Reload", "btn.apply": "apply", "btn.fetchImg": "Fetch image from camera",
      "btn.saveOverride": "Save values (override)", "btn.resetConfig": "Reset to add-on config",
      "btn.distribute": "Distribute evenly", "btn.unify": "Unify",
      "btn.digitPlus": "Digit +", "btn.digitMinus": "Digit −", "btn.reloadImg": "Reload image",
      "btn.savePos": "Save positions", "btn.testRec": "Test recognition"
    }
  };

  var LANG = "de";
  function detectLang() {
    try {
      var s = localStorage.getItem("wz_lang");
      if (s === "de" || s === "en") return s;
    } catch (e) {}
    var n = (navigator.language || "de").toLowerCase();
    return n.indexOf("de") === 0 ? "de" : "en";
  }
  function t(key) {
    var d = I18N[LANG] || I18N.de;
    return (key in d) ? d[key] : (I18N.de[key] !== undefined ? I18N.de[key] : key);
  }
  function applyI18n(root) {
    root = root || document;
    root.querySelectorAll("[data-i18n]").forEach(function (e) { e.textContent = t(e.getAttribute("data-i18n")); });
    root.querySelectorAll("[data-i18n-html]").forEach(function (e) { e.innerHTML = t(e.getAttribute("data-i18n-html")); });
    root.querySelectorAll("[data-i18n-ph]").forEach(function (e) { e.setAttribute("placeholder", t(e.getAttribute("data-i18n-ph"))); });
    root.querySelectorAll("[data-i18n-title]").forEach(function (e) {
      var v = t(e.getAttribute("data-i18n-title")); e.setAttribute("title", v); e.setAttribute("aria-label", v);
    });
  }
  function setLang(l) {
    LANG = (l === "en") ? "en" : "de";
    try { localStorage.setItem("wz_lang", LANG); } catch (e) {}
    document.documentElement.setAttribute("lang", LANG);
    document.querySelectorAll(".lang button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-lang") === LANG);
    });
    applyI18n(document);
    window.dispatchEvent(new CustomEvent("wz:lang", { detail: { lang: LANG } }));
  }
  function providerLabel(p) { return p ? (t("prov." + p) !== "prov." + p ? t("prov." + p) : p) : t("common.none"); }

  /* ------------------------- App-Bar + Navigation ------------------------- */
  var NAV = [
    { id: "overview", href: ".", icon: "dashboard" },
    { id: "config", href: "config", icon: "tune" },
    { id: "tuner", href: "tuner", icon: "crop" },
    { id: "digits", href: "digits", icon: "grid" },
    { id: "cpu", href: "cpu", icon: "memory" },
    { id: "help", href: "help", icon: "help" },
    { id: "info", href: "info", icon: "info" }
  ];
  function activeId() {
    var seg = location.pathname.replace(/\/+$/, "").split("/").pop();
    var ids = ["config", "tuner", "digits", "cpu", "help", "info"];
    return ids.indexOf(seg) >= 0 ? seg : "overview";
  }
  function buildAppbar() {
    var host = document.getElementById("appbar");
    if (!host) return;
    var act = activeId();
    var tabs = NAV.map(function (n) {
      var navKey = n.id === "overview" ? "nav.overview" : "nav." + n.id;
      return '<a class="tab' + (n.id === act ? " active" : "") + '" href="' + n.href +
        '">' + icon(n.icon) + '<span data-i18n="' + navKey + '"></span></a>';
    }).join("");
    host.className = "appbar";
    host.innerHTML =
      '<div class="appbar-inner">' +
        '<span class="brand">' + icon("drop", "drop icon-lg") +
          '<span><h1>Wasserzähler OCR</h1></span></span>' +
        '<span class="spacer"></span>' +
        '<span class="lang" role="group" aria-label="Language">' +
          '<button data-lang="de">DE</button><button data-lang="en">EN</button>' +
        '</span>' +
      '</div>' +
      '<nav class="tabs">' + tabs + '</nav>';
    host.querySelectorAll(".lang button").forEach(function (b) {
      b.addEventListener("click", function () { setLang(b.getAttribute("data-lang")); });
    });
  }

  /* ------------------------------ Ripple ---------------------------------- */
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("button, a.btn");
    if (!b || b.disabled) return;
    var r = b.getBoundingClientRect();
    var d = Math.max(r.width, r.height);
    var s = document.createElement("span");
    s.className = "ripple";
    s.style.width = s.style.height = d + "px";
    s.style.left = (ev.clientX - r.left - d / 2) + "px";
    s.style.top = (ev.clientY - r.top - d / 2) + "px";
    b.appendChild(s);
    setTimeout(function () { s.remove(); }, 500);
  });

  /* ------------------------------ Init ------------------------------------ */
  function init() {
    if (!document.getElementById("wz-sprite")) {
      var wrap = document.createElement("div");
      wrap.id = "wz-sprite";
      wrap.innerHTML = buildSprite();
      document.body.insertBefore(wrap, document.body.firstChild);
    }
    buildAppbar();
    LANG = detectLang();
    setLang(LANG);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();

  /* --------------------------- öffentliche API ---------------------------- */
  window.WZ = { t: t, icon: icon, setLang: setLang, getLang: function () { return LANG; },
    applyI18n: applyI18n, providerLabel: providerLabel };
  window.t = t;
})();
