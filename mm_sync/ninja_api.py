"""
ninja_api.py
Version: 2.0.5
Author: Anthony George

Handles NinjaOne OAuth2, device inventory, and WYSIWYG custom field updates.
"""

import time
import requests

from mm_sync.utils import log, strip_html, load_cache, save_cache
from mm_sync.config import ENDPOINTS, NINJA_CACHE, CACHE_TTL
from mm_sync import secrets


TOKEN_CACHE = {
    "token": None,
    "expires": 0,
}


# -------------------------------------------------------------------------
# INTERNAL: Get OAuth Token
# -------------------------------------------------------------------------
def _fetch_token():
    url = ENDPOINTS["ninja"]["auth"]

    payload = {
        "grant_type": "client_credentials",
        "client_id": secrets.NINJA_CLIENT_ID,
        "client_secret": secrets.NINJA_CLIENT_SECRET,
        "scope": "monitoring management control",
    }

    try:
        r = requests.post(url, data=payload, timeout=20)

        if not r.ok:
            log(f"Ninja token error: {r.status_code} {r.text}", "ERROR")
            return None

        data = r.json()
        TOKEN_CACHE["token"] = data["access_token"]
        TOKEN_CACHE["expires"] = time.time() + data.get("expires_in", 3600) - 30
        return TOKEN_CACHE["token"]

    except Exception as ex:
        log(f"Ninja token exception: {ex}", "ERROR")
        return None


def ninja_token():
    if TOKEN_CACHE["token"] and time.time() < TOKEN_CACHE["expires"]:
        return TOKEN_CACHE["token"]
    return _fetch_token()


# -------------------------------------------------------------------------
# PRE-FLIGHT
# -------------------------------------------------------------------------
def preflight_ninja():
    if ninja_token():
        log("Ninja preflight OK")
        return True
    log("Ninja preflight failed (soft)", "WARN")
    return False


# -------------------------------------------------------------------------
# DEVICE INVENTORY
# -------------------------------------------------------------------------
def pull_ninja_devices():
    cached = load_cache(NINJA_CACHE, CACHE_TTL["ninja"])
    if cached:
        log("Using cached NinjaOne devices")
        return cached

    token = ninja_token()
    if not token:
        log("Ninja devices fetch error: cannot obtain token", "ERROR")
        return []

    url = ENDPOINTS["ninja"]["devices"]

    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=20)

    if not r.ok:
        log("Ninja devices fetch error", "ERROR")
        log(f"  URL: {url}", "ERROR")
        log(f"  HTTP Status: {r.status_code}", "ERROR")
        log(f"  Response: {r.text}", "ERROR")
        return []

    devices = r.json()
    save_cache(NINJA_CACHE, devices)
    return devices


# -------------------------------------------------------------------------
# CUSTOM FIELD UPDATE (WYSIWYG FIX)
# -------------------------------------------------------------------------
def update_custom_field(device_id, field_name, html_value, src_name=None, ninja_name=None):
    """
    Updates a NinjaOne custom field that supports WYSIWYG HTML content.
    Automatically supplies both 'text' and 'html' payloads.
    """

    token = ninja_token()
    if not token:
        return False

    url = ENDPOINTS["ninja"]["custom_fields"].format(id=device_id)

    payload = {
        field_name: {
            "text": strip_html(html_value) or "",
            "html": html_value or ""
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    r = requests.patch(url, json=payload, headers=headers, timeout=20)

    if not r.ok:
        log("Failed updating WYSIWYG custom field", "ERROR")
        log(f"  URL: {url}", "ERROR")
        log(f"  Payload: {payload}", "ERROR")
        log(f"  HTTP Status: {r.status_code}", "ERROR")
        log(f"  Response Body: {r.text}", "ERROR")
        return False

    pretty_src = src_name or "?"
    pretty_ninja = ninja_name or field_name
    log(f"[OK] Updated {field_name} from {pretty_src} → {pretty_ninja} (device {device_id})")

    return True
