"""
=====================================================================
  ninja_sync/api/axcient.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Axcient x360Recover API
=====================================================================

Implements:
  - axcient_get_devices(force=False)
  - preflight_axcient()
"""

import requests

from ..core.logging import log, warn, error
from ..cache import load_cache, save_cache
from ..core.config import (
    AXCIENT_BASE_URL,
    AXCIENT_CACHE_PATH,
)
from ..core.secrets import AXCIENT_API_KEY


# ===============================================================
#  Internal GET helper
# ===============================================================

def _axcient_get(params):
    """Perform a GET request against /device."""
    url = f"{AXCIENT_BASE_URL}/device"
    headers = {"X-Api-Key": AXCIENT_API_KEY}

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        error("Axcient GET failed", url, params, resp)
        return None

    try:
        return resp.json()
    except Exception as e:
        error("Axcient JSON decode failed", url, params, str(e))
        return None


# ===============================================================
#  Main fetch with pagination
# ===============================================================

def axcient_get_devices(force=False):
    cached = load_cache(AXCIENT_CACHE_PATH)
    if cached and not force:
        log("Using cached Axcient data")
        return cached

    log("Fetching Axcient devices (paginated)...")

    all_devices = []
    limit = 100
    offset = 0

    while True:
        batch = _axcient_get({"limit": limit, "offset": offset})
        if not batch or not isinstance(batch, list):
            break

        all_devices.extend(batch)

        # Stop if fewer than limit returned
        if len(batch) < limit:
            break

        offset += limit

    save_cache(AXCIENT_CACHE_PATH, all_devices)
    return all_devices


# ===============================================================
#  Preflight
# ===============================================================

def preflight_axcient():
    log("Preflight: Checking Axcient API...")

    resp = _axcient_get({"limit": 1, "offset": 0})

    if isinstance(resp, list):
        log("Axcient preflight OK")
        return True

    warn("Axcient preflight FAILED (soft)")
    return False
