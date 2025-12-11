"""
ninja_api.py
Version: 2.0.4
Author: Anthony George

Handles NinjaOne OAuth2 authentication and device/custom-field APIs.
"""

import time
import requests

from mm_sync.utils import log, load_cache, save_cache
from mm_sync.config import ENDPOINTS, NINJA_CACHE, CACHE_TTL
from mm_sync import secrets


TOKEN_CACHE = {
    "token": None,
    "expires": 0,
}


# -------------------------------------------------------------------------
# INTERNAL: Request OAuth Token
# -------------------------------------------------------------------------
def _fetch_token():
    url = ENDPOINTS["ninja"]["auth"]

    payload = {
        "grant_type": "client_credentials",
        "client_id": secrets.NINJA_CLIENT_ID,
        "client_secret": secrets.NINJA_CLIENT_SECRET,
        "scope": "monitoring management control",     # REQUIRED
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


# -------------------------------------------------------------------------
# PUBLIC: Get token (cached)
# -------------------------------------------------------------------------
def ninja_token():
    if TOKEN_CACHE["token"] and time.time() < TOKEN_CACHE["expires"]:
        return TOKEN_CACHE["token"]

    return _fetch_token()


# -------------------------------------------------------------------------
# Preflight
# -------------------------------------------------------------------------
def preflight_ninja():
    token = ninja_token()
    if not token:
        log("Ninja preflight failed (soft)", "WARN")
        return False

    log("Ninja preflight OK")
    return True


# -------------------------------------------------------------------------
# Fetch Ninja Devices
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
# Update Custom Field
# -------------------------------------------------------------------------
def update_custom_field(device_id, fields: dict):
    token = ninja_token()
    if not token:
        return False

    url = ENDPOINTS["ninja"]["custom_fields"].format(id=device_id)

    r = requests.post(
        url,
        json=fields,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=20,
    )

    if not r.ok:
        log("Failed updating Ninja custom field", "ERROR")
        log(f"  URL: {url}", "ERROR")
        log(f"  Payload: {fields}", "ERROR")
        log(f"  HTTP Status: {r.status_code}", "ERROR")
        log(f"  Response Body: {r.text}", "ERROR")
        return False

    return True
