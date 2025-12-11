"""
NinjaOne API
Author: Anthony George
Version: 2.0.5
"""

import requests
import datetime
from utils import log, warn, error, load_cache, save_cache, cache_valid, strip_html
from secrets import NINJA_CLIENT_ID, NINJA_CLIENT_SECRET, NINJA_SCOPE
from config import CACHE_PATH, CACHE_TTL_NINJA, FORCE_EXPIRE_NINJA, NINJA_BASE_URL

CACHE_FILE = f"{CACHE_PATH}/ninja_devices.json"
TOKEN_CACHE = f"{CACHE_PATH}/ninja_token.json"

# ------------------------------
# OAuth Token
# ------------------------------
def ninja_get_token():
    cache = load_cache(TOKEN_CACHE)
    if cache_valid(cache, 3000):
        return cache["access_token"]

    url = f"{NINJA_BASE_URL}/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": NINJA_CLIENT_ID,
        "client_secret": NINJA_CLIENT_SECRET,
        "scope": NINJA_SCOPE
    }

    resp = requests.post(url, data=payload)
    if resp.status_code != 200:
        error(f"Ninja token error: {resp.status_code} {resp.text}")
        return None

    token = resp.json().get("access_token")
    save_cache(TOKEN_CACHE, {
        "_timestamp": datetime.datetime.utcnow().isoformat(),
        "access_token": token
    })
    return token


def headers():
    token = ninja_get_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# ------------------------------
# Load devices
# ------------------------------
def pull_ninja_devices():
    if FORCE_EXPIRE_NINJA:
        cache = None
    else:
        cache = load_cache(CACHE_FILE)

    if cache_valid(cache, CACHE_TTL_NINJA):
        log("Using cached NinjaOne devices")
        return cache["devices"]

    url = f"{NINJA_BASE_URL}/v2/devices"
    resp = requests.get(url, headers=headers())

    if resp.status_code != 200:
        error(f"Ninja devices fetch error: {resp.status_code} {resp.text}")
        return []

    devices = resp.json()
    save_cache(CACHE_FILE, {
        "_timestamp": datetime.datetime.utcnow().isoformat(),
        "devices": devices
    })

    return devices


# ------------------------------
# Update custom field
# ------------------------------
def ninja_update_field(device_id, field_name, html, text):
    url = f"{NINJA_BASE_URL}/v2/device/{device_id}/custom-fields"

    payload = {
        field_name: {
            "text": text,
            "html": html
        }
    }

    resp = requests.patch(url, headers=headers(), json=payload)
    if resp.status_code not in (200, 204):
        error(f"Failed updating custom field {field_name} on {device_id}")
        error(resp.text)
        return False

    log(f"[OK] Updated {field_name} on {device_id}")
    return True


def preflight_ninja():
    return ninja_get_token() is not None
