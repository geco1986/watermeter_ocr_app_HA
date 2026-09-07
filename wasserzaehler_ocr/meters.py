"""Registry mehrerer Zaehler (Wasser/Strom/Waerme) fuer das OCR-Add-on.

Jeder Zaehler ist vollstaendig eigenstaendig: eigene Kamera/Lampe, eigener
OCR-Anbieter samt Zugangsdaten und Prompt, eigener Zuschnitt (Tuning),
eigene Ziffern-Boxen, eigener gespeicherter Stand und eigener Verlauf.

Gespeichert wird alles in /data/meters.json:

    {
      "active": "<id>",
      "meters": [
        { "id": "zaehler1", "name": "Wasser", "type": "water",
          <alle ueber die Web-UI einstellbaren Schluessel...> },
        ...
      ]
    }

Zustands-, Verlaufs-, Tuning- und Bilddateien liegen pro Zaehler getrennt
(z. B. /data/state_<id>.json) und werden von app.get_config() adressiert.
"""

import json
import re
from pathlib import Path

import settings

VALID_TYPES = ("water", "electricity", "heat", "gas")
DEFAULT_ID = "zaehler1"


def _slug(name, existing=()):
    """Erzeugt eine datei-/URL-sichere, eindeutige Kennung aus dem Namen."""
    base = re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_") or "zaehler"
    sid, i = base, 2
    while sid in existing:
        sid, i = f"{base}_{i}", i + 1
    return sid


def load(path: Path) -> dict:
    if path.exists():
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and isinstance(data.get("meters"), list):
                return {"active": data.get("active"), "meters": data["meters"]}
        except (OSError, json.JSONDecodeError):
            pass
    return {"active": None, "meters": []}


def save(path: Path, data: dict, log=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.json")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh)
    tmp.replace(path)


def _ensure(d: dict) -> dict:
    """Garantiert mindestens einen Zaehler und ein gueltiges 'active'."""
    if not d["meters"]:
        d["meters"].append({"id": DEFAULT_ID, "name": "Wasser", "type": "water"})
    if not d.get("active") or all(m.get("id") != d["active"] for m in d["meters"]):
        d["active"] = d["meters"][0]["id"]
    return d


def public_list(path: Path) -> list:
    """Discovery-Liste fuer /meters und die Weboberflaeche."""
    d = _ensure(load(path))
    return [{"id": m["id"], "name": m.get("name", m["id"]),
             "type": m.get("type", "water")} for m in d["meters"]]


def active_id(path: Path) -> str:
    return _ensure(load(path))["active"]


def get(path: Path, meter_id):
    for m in _ensure(load(path))["meters"]:
        if m["id"] == meter_id:
            return m
    return None


def resolve(path: Path, meter_id=None) -> dict:
    """Liefert den passenden Zaehler: angeforderte id, sonst aktiver, sonst erster."""
    d = _ensure(load(path))
    if meter_id:
        for m in d["meters"]:
            if m["id"] == meter_id:
                return m
    for m in d["meters"]:
        if m["id"] == d["active"]:
            return m
    return d["meters"][0]


def add(path: Path, name, mtype, log=None) -> dict:
    d = _ensure(load(path))
    ids = {m["id"] for m in d["meters"]}
    sid = _slug(name, ids)
    meter = {"id": sid, "name": (name or sid).strip() or sid,
             "type": mtype if mtype in VALID_TYPES else "water"}
    d["meters"].append(meter)
    d["active"] = sid
    save(path, d, log)
    if log:
        log(f"Zaehler angelegt: {meter['name']} ({sid}, {meter['type']})")
    return meter


def update(path: Path, meter_id, name=None, mtype=None, log=None):
    d = _ensure(load(path))
    for m in d["meters"]:
        if m["id"] == meter_id:
            if name is not None and name.strip():
                m["name"] = name.strip()
            if mtype in VALID_TYPES:
                m["type"] = mtype
            save(path, d, log)
            return m
    return None


def update_settings(path: Path, meter_id, values: dict, log=None):
    """Speichert Web-UI-Einstellungen in den Zaehler (nur erlaubte Schluessel)."""
    d = _ensure(load(path))
    for m in d["meters"]:
        if m["id"] == meter_id:
            for k in settings.SETTINGS_KEYS:
                if k in values:
                    m[k] = values[k]
            save(path, d, log)
            if log:
                safe = {k: ("***" if k in settings.SECRET_KEYS and v else v)
                        for k, v in values.items() if k in settings.SETTINGS_KEYS}
                log(f"Einstellungen fuer {meter_id} gespeichert: {safe}")
            return m
    return None


def delete(path: Path, meter_id, log=None) -> bool:
    """Entfernt einen Zaehler. Der letzte verbleibende wird nicht geloescht."""
    d = _ensure(load(path))
    if len(d["meters"]) <= 1 or all(m["id"] != meter_id for m in d["meters"]):
        return False
    d["meters"] = [m for m in d["meters"] if m["id"] != meter_id]
    if d["active"] == meter_id:
        d["active"] = d["meters"][0]["id"]
    save(path, d, log)
    if log:
        log(f"Zaehler geloescht: {meter_id}")
    return True


def set_active(path: Path, meter_id, log=None) -> bool:
    d = _ensure(load(path))
    if any(m["id"] == meter_id for m in d["meters"]):
        d["active"] = meter_id
        save(path, d, log)
        return True
    return False
