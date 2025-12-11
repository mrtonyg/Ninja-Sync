"""
=====================================================================
  ninja_sync/api/ninja_api.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  NinjaOne API (OAuth2 + v2 endpoints)
=====================================================================

Implements:
  - ninja_get_token(force=False)
  - ninja_get_devices(force=False)
  - ninja_update_custom_field(device_id, field_name, html, src_name, ninja_name)
  - preflight_ninja()
"""

import time
import base64
import requests

from ..core.logging import log, warn, error
from ..config import (
    NINJA_BASE_URL,
    NINJA_TOKEN_CACHE_PATH,
    NINJA_DEVICE_CACHE_PATH,
    NINJA_DEVICE_CACHE_TTL,
)
from ..secrets import (
    NINJA_CLIENT_ID,
    NINJA_CLIENT_SECRET,
)

from ..cache import load_cache, save_cache
from ..html.texttools import strip_html


# ===============================================================
#  OAuth2 Token Handling
# ===============================================================

def ninja_get_token(force=False):
    cached = load_cache(NINJA_TOKEN_CACHE_PATH)
    if cached and not force:
        expires_at = cached.get("expires_at", 0)
        if time.time() < expires_at:
            return cached["access_token"]

    token_url = f"{NINJA_BASE_URL}/oauth/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": NINJA_CLIENT_ID,
        "client_secret": NINJA_CLIENT_SECRET,
        "scope": "monitoring management control",
    }

    resp = requests.post(token_url, data=payload)

    if resp.status_code != 200:
        error("Ninja token error", token_url, payload, resp)
        return None

    data = resp.json()
    token = data.get("access_token")
    expires_in = data.get("expires_in", 3600)

    save_cache(
        NINJA_TOKEN_CACHE_PATH,
        {"access_token": token, "expires_at": time.time() + expires_in - 60}
    )

    return token


# ===============================================================
#  Device Fetch
# ===============================================================

def ninja_get_devices(force=False):
    cached = load_cache(NINJA_DEVICE_CACHE_PATH)
    if cached and not force:
        log("Using cached NinjaOne devices")
        return cached

    token = ninja_get_token()
    if not token:
        warn("Cannot fetch Ninja devices — no token")
        return []

    url = f"{NINJA_BASE_URL}/v2/devices"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        error("Ninja devices fetch error", url, None, resp)
        return []

    devices = resp.json()
    save_cache(NINJA_DEVICE_CACHE_PATH, devices)
    return devices


# ===============================================================
#  Update Custom Field (WYSIWYG-Compatible)
# ===============================================================

def ninja_update_custom_field(device_id, field_name, html, src_name, ninja_name):
    """
    Required formatting for WYSIWYG fields:
        {
          "fieldName": {
             "text": "...plaintext...",
             "html": "<p>formatted...</p>"
          }
        }
    """

    token = ninja_get_token()
    if not token:
        warn(f"Cannot update field {field_name} on {device_id} — no token")
        return False

    url = f"{NINJA_BASE_URL}/v2/device/{device_id}/custom-fields"
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        field_name: {
            "text": strip_html(html),
            "html": html
        }
    }

    resp = requests.patch(url, headers=headers, json=payload)

    # 200 or 204 = accepted
    if resp.status_code not in (200, 204):
        error(f"Failed updating {field_name}", url, payload, resp)
        return False

    log(f"[OK] Updated {field_name} → {src_name} → NinjaOne: {ninja_name} ({device_id})")
    return True


# ===============================================================
#  Preflight
# ===============================================================

def preflight_ninja():
    log("Preflight: Checking NinjaOne API...")

    token = ninja_get_token(force=True)
    if not token:
        warn("Ninja preflight FAILED (soft)")
        return False

    # Try to pull 1 device
    devices = ninja_get_devices(force=True)
    if isinstance(devices, list):
        log("Ninja preflight OK")
        return True

    warn("Ninja preflight FAILED (soft)")
    return False
