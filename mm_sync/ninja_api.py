"""
ninja_api.py
Version: 2.0.1
Author: Anthony George
"""

import requests
from mm_sync.utils import log, load_cache, save_cache
from mm_sync.config import ENDPOINTS, NINJA_CACHE, CACHE_TTL
from mm_sync import secrets


# -------------------------------------------------------------------------
# OAuth2 Token
# -------------------------------------------------------------------------
def ninja_get_token():
    url = ENDPOINTS["ninja"]["auth"]
    payload = {
        "grant_type": "client_credentials",
        "client_id": secrets.NINJA_CLIENT_ID,
        "client_secret": secrets.NINJA_CLIENT_SECRET,
    }

    r = requests.post(url, data=payload)
    if not r.ok:
        log(f"Ninja token error: {r.status_code} {r.text}", "ERROR")
        return None

    return r.json().get("access_token")


# -------------------------------------------------------------------------
# Preflight Check
# -------------------------------------------------------------------------
def preflight_ninja():
    token = ninja_get_token()
    if not token:
        log("Ninja preflight failed (soft)", "WARN")
        return False
    log("Ninja preflight OK")
    return True


# -------------------------------------------------------------------------
# Pull devices (cached)
# -------------------------------------------------------------------------
def pull_ninja_devices():
    cached = load_cache(NINJA_CACHE, CACHE_TTL["ninja"])
    if cached:
        log("Using cached NinjaOne devices")
        return cached

    token = ninja_get_token()
    if not token:
        return []

    url = ENDPOINTS["ninja"]["devices"]
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})

    if not r.ok:
        log(f"Ninja device fetch error {r.status_code}: {r.text}", "ERROR")
        return []

    devices = r.json()
    save_cache(NINJA_CACHE, devices)
    return devices


# -------------------------------------------------------------------------
# Update Custom Field
# -------------------------------------------------------------------------
def update_custom_field(device_id, json_payload):
    token = ninja_get_token()
    if not token:
        return False

    url = ENDPOINTS["ninja"]["custom_fields"].format(id=device_id)
    r = requests.post(url,
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json=json_payload)

    if not r.ok:
        log(f"Custom field update failed {device_id}: {r.status_code} {r.text}",
            "ERROR")
        return False

    return True
