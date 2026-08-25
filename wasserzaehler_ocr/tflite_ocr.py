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


def _digit_from_vec(vec):
    """Bildet einen Ausgabevektor auf (ziffer|None, konfidenz 0..1) ab.

    ziffer ist None, wenn das Modell "unklar" meldet (NaN-Klasse bei class11).
    """
    n = len(vec)
    idx = int(max(range(n), key=lambda i: vec[i]))
    mx = float(vec[idx])
    ssum = float(sum(v for v in vec if v > 0)) or float(sum(abs(v) for v in vec)) or 1.0
    conf = max(0.0, min(1.0, mx / ssum))
    if n == 11:
        digit = None if idx == 10 else idx
    elif n == 100:
        digit = idx // 10
    elif n == 10:
        digit = idx
    else:
        digit = int(round(idx * 9.0 / max(1, n - 1))) % 10
    return digit, conf


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
              rois=None, with_crops=False):
    """Erkennt den Zaehler ziffernweise.

    Nutzt die per ROI definierten Ziffern-Boxen (AI-on-the-edge-Stil), sonst
    gleichmaessige Streifen. Rueckgabe:
      (digits_or_None, details, error)
    ``details`` ist eine Liste pro Ziffer mit: index, value (int|None),
    label ("0".."9" oder "NaN"), confidence (0..1), box (x,y,w,h normiert)
    und (falls with_crops) thumb (data-URL des Ausschnitts).
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

    details = []
    digits = []
    all_valid = True
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        crop = img.crop((x0, y0, x1, y1))
        model_in = crop.resize((int(in_w), int(in_h)), Image.LANCZOS)
        arr = np.asarray(model_in, dtype=np.float32).reshape(1, int(in_h), int(in_w), 3)
        interp.set_tensor(in_det["index"], arr)
        interp.invoke()
        vec = interp.get_tensor(out_det["index"])[0].tolist()
        digit, conf = _digit_from_vec(vec)

        if digit is None:
            all_valid = False
            label = "NaN"
        else:
            label = str(digit)
            digits.append(str(digit))

        box_norm = {"x": round(x0 / W, 4), "y": round(y0 / H, 4),
                    "w": round((x1 - x0) / W, 4), "h": round((y1 - y0) / H, 4)}
        if use_rois and sorted_rois and i < len(sorted_rois):
            src = sorted_rois[i]
            box_norm = {"x": float(src.get("x", box_norm["x"])),
                        "y": float(src.get("y", box_norm["y"])),
                        "w": float(src.get("w", box_norm["w"])),
                        "h": float(src.get("h", box_norm["h"]))}

        det = {"index": i, "value": digit, "label": label,
               "confidence": round(conf, 3), "box": box_norm}
        if with_crops:
            import base64, io as _io
            thumb = crop.resize((28, 46), Image.LANCZOS)
            b = _io.BytesIO()
            thumb.save(b, "PNG")
            det["thumb"] = "data:image/png;base64," + \
                base64.b64encode(b.getvalue()).decode("ascii")
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
        log(f"TFLite ({model_path.name}): erkannt '{digits_str}' "
            f"({'ROIs' if use_rois else 'gleichmäßig'}, {len(boxes)} Ziffern)")
    return (digits_str if valid else None), details, err


def read_digits(image_path, model_name, main_digits, decimal_digits, log, rois=None):
    """Kompatibler Aufruf fuer den OCR-Provider. Rueckgabe (digits, error)."""
    digits, _details, err = recognize(
        image_path, model_name, main_digits, decimal_digits, log, rois=rois)
    return digits, err
