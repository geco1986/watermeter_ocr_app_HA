"""Bildabruf von der Home-Assistant-Kamera-Entitaet.

Nutzt den camera_proxy-Endpunkt der HA-API. Das Add-on bekommt vom
Supervisor automatisch ein Token in der Umgebungsvariable SUPERVISOR_TOKEN,
mit dem der Zugriff auf http://supervisor/core/api/... erlaubt ist.
"""

import os
from pathlib import Path

import requests

SUPERVISOR_API = "http://supervisor/core/api"


def _call_service(domain: str, service: str, entity_id: str, timeout: int, log,
                  data: dict = None):
    """Ruft einen HA-Service auf, z. B. light.turn_on / switch.turn_off.

    ``data`` wird zusaetzlich in die Payload gemischt (z. B. brightness_pct).
    """
    token = os.environ.get("SUPERVISOR_TOKEN")
    if not token:
        raise RuntimeError(
            "SUPERVISOR_TOKEN fehlt - laeuft das Add-on mit homeassistant_api: true?"
        )
    url = f"{SUPERVISOR_API}/services/{domain}/{service}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"entity_id": entity_id}
    if data:
        payload.update(data)
    resp = requests.post(
        url, headers=headers, json=payload, timeout=timeout
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"Service {domain}.{service} fuer {entity_id} fehlgeschlagen "
            f"(HTTP {resp.status_code})."
        )


def set_light(entity_id: str, on: bool, timeout: int, log, brightness_pct=None):
    """Schaltet die Lampe der Kamera ein oder aus.

    Domaene (light/switch) wird aus der Entity-ID abgeleitet. Fehler beim
    Ausschalten werden nur geloggt, nicht geworfen - das Bild ist wichtiger.

    ``brightness_pct`` (1-100) wird nur beim Einschalten und nur fuer
    light-Entitaeten mitgesendet. 0 oder None = ohne Helligkeitsvorgabe.
    """
    if not entity_id:
        return  # keine Lampe konfiguriert -> nichts tun

    domain = entity_id.split(".", 1)[0]
    if domain not in ("light", "switch"):
        log(f"WARNUNG: Lampe '{entity_id}' hat unerwartete Domaene '{domain}', "
            f"versuche es trotzdem.")

    service = "turn_on" if on else "turn_off"
    data = None
    if on and domain == "light" and brightness_pct:
        try:
            pct = int(brightness_pct)
        except (TypeError, ValueError):
            pct = 0
        if 1 <= pct <= 100:
            data = {"brightness_pct": pct}
    try:
        _call_service(domain, service, entity_id, timeout, log, data=data)
        extra = f" ({data['brightness_pct']}%)" if data else ""
        log(f"Lampe {entity_id} -> {'AN' + extra if on else 'AUS'}")
    except Exception as exc:
        log(f"WARNUNG: Lampe schalten fehlgeschlagen: {exc}")


def fetch_camera_image(camera_entity: str, dst_path: Path, timeout: int, log):
    """Holt ein aktuelles Bild der Kamera-Entitaet und speichert es.

    Gibt dst_path zurueck. Wirft Exceptions bei Fehlern.
    """
    token = os.environ.get("SUPERVISOR_TOKEN")
    if not token:
        raise RuntimeError(
            "SUPERVISOR_TOKEN fehlt - laeuft das Add-on mit homeassistant_api: true?"
        )

    url = f"{SUPERVISOR_API}/camera_proxy/{camera_entity}"
    headers = {"Authorization": f"Bearer {token}"}

    log(f"Hole Bild von {camera_entity} ...")
    resp = requests.get(url, headers=headers, timeout=timeout)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Kamera-Abruf fehlgeschlagen (HTTP {resp.status_code}). "
            f"Existiert die Entitaet '{camera_entity}' und liefert sie ein Bild?"
        )

    content = resp.content
    if not content:
        raise RuntimeError(f"Kamera '{camera_entity}' lieferte ein leeres Bild.")

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst_path.with_suffix(".download.jpg")
    tmp.write_bytes(content)
    tmp.replace(dst_path)

    log(f"Bild gespeichert: {dst_path.name} ({len(content)} Bytes)")
    return dst_path
