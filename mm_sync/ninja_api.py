# ninja_api.py
# NinjaOne OAuth2, device inventory, custom field updates, caching.

import time
import requests
import os

from .secrets import (
    NINJA_CLIENT_ID,
    NINJA_CLIENT_SECRET
)
from .config import (
    NINJA_CACHE_DIR,
    CACHE_TTL_NINJA
)
from .utils import (
    log, log_error,
    json_load, json_save
)

# ------------------------------------------------------------
# Cache paths
# ------------------------------------------------------------
TOKEN_CACHE = os.path.join(NINJA_CACHE_DIR, "token.json")
DEVICES_CACHE = os.path.join(NINJA_CACHE_DIR, "devices.json")
TS_CACHE = os.path.join(NINJA_CACHE_DIR, "timestamp.json")

BASE_URL = "https://app.ninjarmm.com"

# ------------------------------------------------------------
# OAuth2 token handling
# ------------------------------------------------------------
def token_valid():
    tok = json_load(TOKEN_CACHE)
    if not tok:
        return False
    exp = tok.get("expires_at", 0)
    return time.time() < exp

def fetch_token():
    url = f"{BASE_URL}/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": NINJA_CLIENT_ID,
        "client_secret": NINJA_CLIENT_SECRET
    }
    try:
        resp = requests.post(url, data=data)
        if resp.status_code != 200:
            log_error("Ninja token error", url, data, resp)
            return None
        js = resp.json()
        js["expires_at"] = time.time() + js.get("expires_in", 3600)
        json_save(TOKEN_CACHE, js)
        log("[INFO] Obtained new NinjaOne OAuth token")
        return js
    except Exception as e:
        log_error("Ninja token exception", url, data, exc=e)
        return None

def ninja_get_token():
    if token_valid():
        tok = json_load(TOKEN_CACHE)
        return tok.get("access_token")
    tok = fetch_token()
    return tok.get("access_token") if tok else None

def ninja_headers():
    return {
        "Authorization": f"Bearer {ninja_get_token()}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

# ------------------------------------------------------------
# Device inventory
# ------------------------------------------------------------
def devices_cache_valid():
    ts = json_load(TS_CACHE)
    if not ts:
        return False
    return (time.time() - ts.get("timestamp",0)) < CACHE_TTL_NINJA

def ninja_save_devices(devs):
    os.makedirs(NINJA_CACHE_DIR, exist_ok=True)
    json_save(DEVICES_CACHE, devs)
    json_save(TS_CACHE, {"timestamp": time.time()})

def ninja_load_devices():
    d = json_load(DEVICES_CACHE)
    return d if d else None

def ninja_get_all_devices(force_refresh=False):
    if not force_refresh and devices_cache_valid():
        d = ninja_load_devices()
        if d:
            log("[INFO] Using cached NinjaOne devices")
            return d

    url = f"{BASE_URL}/v2/devices"
    try:
        resp = requests.get(url, headers=ninja_headers())
        if resp.status_code != 200:
            log_error("Ninja devices fetch error", url, None, resp)
            return []
        devs = resp.json()
        ninja_save_devices(devs)
        return devs
    except Exception as e:
        log_error("Ninja devices exception", url, exc=e)
        return []

# ------------------------------------------------------------
# Update custom field
# ------------------------------------------------------------
def ninja_update_field(device_id, field_name, html, huntress_name, ninja_name):
    url = f"{BASE_URL}/v2/device/{device_id}/custom-fields"
    payload = {field_name: html}

    try:
        resp = requests.put(url, headers=ninja_headers(), json=payload)
        if resp.status_code not in (200,204):
            log_error(f"Failed updating Ninja custom field", url, payload, resp)
            return False

        log(f"[OK] Updated {field_name} for device {device_id} ({huntress_name} → {ninja_name})")
        return True

    except Exception as e:
        log_error("Exception updating custom field", url, payload, exc=e)
        return False
