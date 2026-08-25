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


def _digit_from_output(vec):
    """Bildet den Ausgabevektor auf eine Ziffer 0-9 ab.

    Rueckgabe: int 0-9, oder None wenn das Modell "unklar" meldet (NaN-Klasse).
    """
    n = len(vec)
    idx = int(max(range(n), key=lambda i: vec[i]))
    if n == 11:
        return None if idx == 10 else idx
    if n == 100:
        return idx // 10
    if n == 10:
        return idx
    # Fallback: linear auf 0-9 skalieren
    return int(round(idx * 9.0 / max(1, n - 1))) % 10


def read_digits(image_path, model_name, main_digits, decimal_digits, log):
    """Liest den Zaehler ziffernweise mit dem gewaehlten TFLite-Modell.

    Rueckgabe:
      (ziffernstring, None)  bei Erfolg, z. B. ("01260624", None)
      (None, fehlertext)     bei Problemen
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        return None, f"TFLite-Abhängigkeit fehlt: {exc}"

    model_path = resolve_model(model_name)
    if model_path is None:
        return None, f"TFLite-Modell nicht gefunden: {model_name!r}"

    try:
        interp = _load_interpreter(model_path)
    except Exception as exc:  # noqa: BLE001
        return None, f"TFLite-Runtime nicht verfügbar ({exc})"

    in_det = interp.get_input_details()[0]
    out_det = interp.get_output_details()[0]
    _, in_h, in_w, _ = in_det["shape"]

    total = main_digits + decimal_digits
    if total <= 0:
        return None, "Anzahl Ziffern ist 0 – bitte in der Konfiguration setzen"

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        return None, f"Bild konnte nicht geöffnet werden: {exc}"

    W, H = img.size
    digits = []
    for i in range(total):
        x0 = round(i * W / total)
        x1 = round((i + 1) * W / total)
        slice_img = img.crop((x0, 0, max(x0 + 1, x1), H)).resize(
            (int(in_w), int(in_h)), Image.LANCZOS)
        # AI-on-the-edge-Konvention: RGB-Werte 0..255 als float32
        arr = np.asarray(slice_img, dtype=np.float32)
        arr = arr.reshape(1, int(in_h), int(in_w), 3)
        interp.set_tensor(in_det["index"], arr)
        interp.invoke()
        vec = interp.get_tensor(out_det["index"])[0].tolist()
        d = _digit_from_output(vec)
        if d is None:
            log(f"TFLite: Ziffer {i + 1}/{total} unklar (Modell meldet NaN)")
            return None, f"Ziffer {i + 1} unklar (Modell: NaN)"
        digits.append(str(d))

    result = "".join(digits)
    log(f"TFLite ({model_path.name}): erkannt {result!r}")
    return result, None
