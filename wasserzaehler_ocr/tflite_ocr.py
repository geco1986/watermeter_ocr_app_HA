"""Lokale Ziffernerkennung mit TFLite-Modellen (AI-on-the-edge-Stil).

Jedes Modell erkennt EINE einzelne Ziffer aus einem 32x20-RGB-Ausschnitt.
Um einen ganzen Zaehler zu lesen, wird der (bereits per Tuner zugeschnittene)
Zahlenausschnitt in ``main+decimal`` gleich breite Streifen geteilt; jeder
Streifen wird einzeln klassifiziert und die Ziffern werden zusammengesetzt.

Modelle liegen in einem eigenen Ordner:
  - mitgeliefert im Image unter ``/app/models`` (BUNDLED_DIR)
  - zusaetzlich benutzereigene Modelle unter ``/data/models`` (USER_DIR,
    bleibt ueber Updates erhalten)
``list_models()`` zeigt die Vereinigung beider Ordner (nach Dateiname
dedupliziert), damit in der Konfiguration alles auftaucht, was vorhanden ist.

Die verschiedenen Modelltypen werden generisch ueber die Laenge des
Ausgabevektors behandelt:
  - 11 Klassen (dig-class11): 0-9 und Index 10 = "unklar"/NaN
  - 100 Klassen (dig-class100): Wert 0.0-9.9, Ziffer = argmax // 10
  - 10 Werte (dig-cont / class10): Ziffer = argmax
  - sonst: bestmoegliche Skalierung auf 0-9
"""

from pathlib import Path

BUNDLED_DIR = Path(__file__).resolve().parent / "models"
USER_DIR = Path("/data/models")

# Interpreter-Cache: {pfad: (mtime, interpreter)}
_CACHE = {}


def _dirs():
    return [USER_DIR, BUNDLED_DIR]


def ensure_dirs():
    """Legt den benutzereigenen Modellordner an (best effort)."""
    try:
        USER_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


def list_models():
    """Alle *.tflite-Dateien aus User- und Bundled-Ordner (dedupliziert)."""
    ensure_dirs()
    seen = {}
    for d in _dirs():
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.tflite")):
            seen.setdefault(p.name, p)  # USER_DIR hat Vorrang (zuerst durchlaufen)
    return sorted(seen.keys())


def resolve_model(name):
    """Findet den Pfad zu einem Modellnamen (User-Ordner vor Bundled)."""
    name = (name or "").strip()
    if not name:
        return None
    for d in _dirs():
        p = d / name
        if p.is_file():
            return p
    return None


def _load_interpreter(model_path):
    """Laedt (und cacht) einen TFLite-Interpreter. Erwartet ein installiertes
    Runtime-Paket (ai-edge-litert oder tflite-runtime)."""
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        try:
            from tflite_runtime.interpreter import Interpreter
        except ImportError:
            from tensorflow.lite import Interpreter  # letzter Fallback

    key = str(model_path)
    mtime = model_path.stat().st_mtime
    cached = _CACHE.get(key)
    if cached and cached[0] == mtime:
        return cached[1]

    interp = Interpreter(model_path=str(model_path))
    interp.allocate_tensors()
    _CACHE[key] = (mtime, interp)
    return interp


def _class11_digit(vec):
    """dig-class11: Index 0-9 = Ziffer, 10 = 'N' (unklar). (ziffer|None, konf)."""
    n = len(vec)
    idx = int(max(range(n), key=lambda i: vec[i]))
    mx = float(vec[idx])
    ssum = float(sum(v for v in vec if v > 0)) or 1.0
    conf = max(0.0, min(1.0, mx / ssum))
    return (None if idx == 10 else idx), conf


def _continuous_value(vec):
    """dig-cont / dig-class100: Ausgabevektor -> kontinuierlicher Wert 0..10.

    Die Ausgaben werden als Gewichte auf einem Kreis der Laenge n aufgefasst
    (die Ziffern 0..9 bzw. 0.0..9.9 sind zyklisch: nach 9 kommt wieder 0). Der
    zirkulaere Mittelwert liefert eine Zwischenstellung (z. B. 6.8) - genau die
    hohe Aufloesung, die AI-on-the-edge nutzt. Zusaetzlich: Konfidenz 0..1
    (Konzentration der Verteilung).
    """
    import math
    n = len(vec)
    w = [v if v > 0 else 0.0 for v in vec]
    s = sum(w)
    if s <= 0:
        w = [1.0] * n
        s = float(n)
    sin_s = sum(w[i] * math.sin(2 * math.pi * i / n) for i in range(n))
    cos_s = sum(w[i] * math.cos(2 * math.pi * i / n) for i in range(n))
    ang = math.atan2(sin_s, cos_s)
    if ang < 0:
        ang += 2 * math.pi
    pos = ang / (2 * math.pi) * n          # [0, n)
    value = (pos / n * 10.0) % 10.0        # [0, 10)
    conf = math.hypot(sin_s, cos_s) / s    # 0..1 (Laenge des Resultierenden)
    return value, max(0.0, min(1.0, conf))


def _apply_rollover(values):
    """Nachbarziffer-/Nulldurchgangs-Korrektur (AI-on-the-edge-Prinzip).

    ``values`` sind kontinuierliche Werte 0..10 pro Ziffer, links = hoechstwertig.
    Von rechts nach links: die niederwertigste Ziffer wird gerundet; jede
    hoehere Ziffer wird nur dann aufgerundet, wenn sie im Uebergang ist
    (Nachkommateil >= 0.5) UND die Ziffer rechts bereits durch Null ist
    (< 5) - sonst wird abgerundet. So wird z. B. '17.9' zu '16.9' korrigiert,
    solange die Unterziffer die Null noch nicht ueberschritten hat.
    """
    import math
    n = len(values)
    res = [0] * n
    res[n - 1] = int(round(values[n - 1])) % 10
    for i in range(n - 2, -1, -1):
        v = values[i]
        base = int(math.floor(v)) % 10
        frac = v - math.floor(v)
        sub = values[i + 1]
        if frac >= 0.5 and sub < 5.0:
            base = (base + 1) % 10
        res[i] = base
    return res


def _boxes_from_rois(rois, W, H):
    """Normierte ROIs (0..1) -> Pixel-Boxen (x0,y0,x1,y1), von links nach rechts."""
    boxes = []
    for r in sorted(rois, key=lambda r: float(r.get("x", 0))):
        x0 = int(round(float(r.get("x", 0)) * W))
        y0 = int(round(float(r.get("y", 0)) * H))
        x1 = int(round((float(r.get("x", 0)) + float(r.get("w", 0))) * W))
        y1 = int(round((float(r.get("y", 0)) + float(r.get("h", 0))) * H))
        x0, x1 = max(0, min(x0, W - 1)), max(1, min(x1, W))
        y0, y1 = max(0, min(y0, H - 1)), max(1, min(y1, H))
        if x1 <= x0:
            x1 = x0 + 1
        if y1 <= y0:
            y1 = y0 + 1
        boxes.append((x0, y0, x1, y1))
    return boxes


def _boxes_equal(total, W, H):
    """Gleichmaessige Streifen (Fallback, wenn keine ROIs definiert sind)."""
    boxes = []
    for i in range(total):
        x0 = round(i * W / total)
        x1 = round((i + 1) * W / total)
        boxes.append((x0, 0, max(x0 + 1, x1), H))
    return boxes


def recognize(image_path, model_name, main_digits, decimal_digits, log,
              rois=None, with_crops=False, input_range="0-255", rollover_fix=True):
    """Erkennt den Zaehler ziffernweise.

    input_range: "0-255" (AI-on-the-edge-Standard) oder "0-1" (Werte /255).
    rollover_fix: Nachbarziffer-Korrektur fuer Rollenzaehlwerke (nur bei
      kontinuierlichen Modellen dig-cont/dig-class100 wirksam).

    Rueckgabe: (digits_or_None, details, error). ``details`` pro Ziffer:
    index, value (int|None), raw (float|None), label, confidence, box, [thumb].
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        return None, [], f"TFLite-Abhängigkeit fehlt: {exc}"

    model_path = resolve_model(model_name)
    if model_path is None:
        return None, [], f"TFLite-Modell nicht gefunden: {model_name!r}"
    try:
        interp = _load_interpreter(model_path)
    except Exception as exc:  # noqa: BLE001
        return None, [], f"TFLite-Runtime nicht verfügbar ({exc})"

    in_det = interp.get_input_details()[0]
    out_det = interp.get_output_details()[0]
    _, in_h, in_w, _ = in_det["shape"]
    out_len = int(out_det["shape"][-1])
    is_class11 = (out_len == 11)

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        return None, [], f"Bild konnte nicht geöffnet werden: {exc}"
    W, H = img.size

    use_rois = bool(rois)
    total = main_digits + decimal_digits
    if use_rois:
        sorted_rois = sorted(rois, key=lambda r: float(r.get("x", 0)))
        boxes = _boxes_from_rois(rois, W, H)
    else:
        if total <= 0:
            return None, [], "Anzahl Ziffern ist 0 – bitte in der Konfiguration setzen"
        sorted_rois = None
        boxes = _boxes_equal(total, W, H)

    # 1. Pro Box das Modell auswerten -> Rohwerte sammeln
    raws = []       # kontinuierlicher Wert 0..10 (oder None bei class11)
    confs = []
    crops = []
    for (x0, y0, x1, y1) in boxes:
        crop = img.crop((x0, y0, x1, y1))
        crops.append(crop)
        model_in = crop.resize((int(in_w), int(in_h)), Image.LANCZOS)
        arr = np.asarray(model_in, dtype=np.float32)
        if input_range == "0-1":
            arr = arr / 255.0
        arr = arr.reshape(1, int(in_h), int(in_w), 3)
        interp.set_tensor(in_det["index"], arr)
        interp.invoke()
        vec = interp.get_tensor(out_det["index"])[0].tolist()
        if is_class11:
            digit, conf = _class11_digit(vec)
            raws.append(None if digit is None else float(digit))
            confs.append(conf)
        else:
            value, conf = _continuous_value(vec)
            raws.append(value)
            confs.append(conf)

    # 2. Zu Ganzzahlen zusammensetzen
    if is_class11:
        int_digits = [None if r is None else int(r) % 10 for r in raws]
    else:
        if rollover_fix and len(raws) >= 2:
            int_digits = _apply_rollover(raws)
        else:
            int_digits = [int(round(r)) % 10 for r in raws]

    # 3. Details + Ziffernstring
    details = []
    digits = []
    all_valid = True
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        d = int_digits[i]
        if d is None:
            all_valid = False
            label = "NaN"
        else:
            label = str(d)
            digits.append(str(d))
        box_norm = {"x": round(x0 / W, 4), "y": round(y0 / H, 4),
                    "w": round((x1 - x0) / W, 4), "h": round((y1 - y0) / H, 4)}
        if use_rois and sorted_rois and i < len(sorted_rois):
            s = sorted_rois[i]
            box_norm = {"x": float(s.get("x", box_norm["x"])), "y": float(s.get("y", box_norm["y"])),
                        "w": float(s.get("w", box_norm["w"])), "h": float(s.get("h", box_norm["h"]))}
        det = {"index": i, "value": d, "label": label,
               "raw": (None if raws[i] is None else round(raws[i], 2)),
               "confidence": round(confs[i], 3), "box": box_norm}
        if with_crops:
            import base64, io as _io
            thumb = crops[i].resize((28, 46), Image.LANCZOS)
            b = _io.BytesIO()
            thumb.save(b, "PNG")
            det["thumb"] = "data:image/png;base64," + base64.b64encode(b.getvalue()).decode("ascii")
        details.append(det)

    digits_str = "".join(digits) if digits else ""
    valid = all_valid and len(boxes) == total and total > 0
    err = None
    if not valid:
        if not all_valid:
            bad = [d["index"] + 1 for d in details if d["value"] is None]
            err = f"Ziffer(n) unklar (Modell: NaN): {bad}"
        elif len(boxes) != total:
            err = f"erwartet {total} Ziffern, definiert {len(boxes)}"
    if log:
        log(f"TFLite ({model_path.name}): '{digits_str}' "
            f"[{'class11' if is_class11 else 'kontinuierlich'}, "
            f"Norm {input_range}, Rollover {'an' if (rollover_fix and not is_class11) else 'aus'}, "
            f"{len(boxes)} Ziffern]")
    return (digits_str if valid else None), details, err


def read_digits(image_path, model_name, main_digits, decimal_digits, log,
                rois=None, input_range="0-255", rollover_fix=True):
    """Kompatibler Aufruf fuer den OCR-Provider. Rueckgabe (digits, error)."""
    digits, _details, err = recognize(
        image_path, model_name, main_digits, decimal_digits, log,
        rois=rois, input_range=input_range, rollover_fix=rollover_fix)
    return digits, err
