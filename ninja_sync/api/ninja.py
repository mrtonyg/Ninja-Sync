"""
=====================================================================
  ninja_sync/api/ninja.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  NinjaOne API Client
=====================================================================

Implements:
  - ninja_get_token(force=False)
  - ninja_get_devices(force=False)
  - ninja_update_field(device_id, field_name, html, src_name, ninja_name)
  - preflight_ninja()
"""

import time
import requests

from ..core.logging import log, warn, error
from ..cache import load_cache, save_cache
from ..config import (
    NINJA_BASE_URL,
    NINJA_CACHE_PATH,
)
from ..secrets import (
    NINJA_CLIENT_ID,
    NINJA_CLIENT_SECRET,
)
from ..core.html_builder import strip_html


# ============================================================
# Token handling
# ============================================================

TOKEN_CACHE = {
    "token": None,
    "expires": 0,
}

SCOPES = "monitoring management control"


def ninja_get_token(force=False):
    """Retrieve a NinjaOne OAuth2 token, cached."""
    now = time.time()

    if TOKEN_CACHE["token"] and TOKEN_CACHE["expires"] > now and not force:
        return TOKEN_CACHE["token"]

    url = f"{NINJA_BASE_URL}/oauth/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": NINJA_CLIENT_ID,
        "client_secret": NINJA_CLIENT_SECRET,
        "scope": SCOPES,
    }

    resp = requests.post(url, data=payload)

    if resp.status_code != 200:
        error("Ninja token error",
              url=url,
              params=payload,
              resp=resp)
        return None

    data = resp.json()
    token = data.get("access_token")
    expires_in = data.get("expires_in", 300)

    TOKEN_CACHE["token"] = token
    TOKEN_CACHE["expires"] = now + expires_in - 5
    return token


def _headers():
    token = ninja_get_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


# ============================================================
# Device retrieval
# ============================================================

def ninja_get_devices(force=False):
    cached = load_cache(NINJA_CACHE_PATH)
    if cached and not force:
        log("Using cached NinjaOne devices")
        return cached

    url = f"{NINJA_BASE_URL}/v2/devices"
    resp = requests.get(url, headers=_headers())

    if resp.status_code != 200:
        error("Ninja devices fetch error",
              url=url,
              resp=resp)
        return {}

    try:
        devices = resp.json()
    except Exception as e:
        error("Ninja device JSON decode error", str(e))
        return {}

    save_cache(NINJA_CACHE_PATH, devices)
    return devices


# ============================================================
# Custom-field update (WYSIWYG)
# ============================================================

def ninja_update_field(device_id, field_name, html, src_name, ninja_name):
    """
    Fully correct NinjaOne WYSIWYG update:

       {
         "<field_name>": {
             "text": "plain text...",
             "html": "<b>formatted text</b>"
         }
       }
    """

    url = f"{NINJA_BASE_URL}/v2/device/{device_id}/custom-fields"

    payload = {
        field_name: {
            "text": strip_html(html),
            "html": html,
        }
    }

    resp = requests.patch(url, headers=_headers(), json=payload)

    if resp.status_code not in (200, 204):
        error(f"Failed updating {field_name}",
              url=url,
              params=payload,
              resp=resp)
        return False

    log(f"[OK] Updated {field_name} :: {src_name} → {ninja_name} ({device_id})")
    return True


# ============================================================
# Preflight
# ============================================================

def preflight_ninja():
    log("Preflight: Checking NinjaOne credentials...")

    token = ninja_get_token(force=True)
    if not token:
        warn("Ninja preflight FAILED (soft)")
        return False

    url = f"{NINJA_BASE_URL}/v2/devices"
    resp = requests.get(url, headers=_headers())

    if resp.status_code == 200:
        log("Ninja preflight OK")
        return True

    warn("Ninja preflight FAILED (soft)")
    error("Ninja device fetch failure", url=url, resp=resp)
    return False
