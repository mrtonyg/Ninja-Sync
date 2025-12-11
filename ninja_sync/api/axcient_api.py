"""
=====================================================================
  ninja_sync/api/axcient_api.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Axcient x360Recover API Integration
=====================================================================

Implements:
  - axcient_get(endpoint, params=None)
  - fetch_all_axcient_devices(force=False)
  - preflight_axcient()
"""

from ..core.logging import log, warn, error
from ..core.config import (
    AXCIENT_BASE_URL,
    AXCIENT_CACHE_PATH_DEVICES,
    AXCIENT_PAGE_SIZE,
)
from ..core.secrets import AXCIENT_API_KEY
from .base_api import api_get_json
from ninja_sync.core.cache import read_cache, write_cache, clear_cache, clear_cache_group


# ---------------------------------------------------------------------
#  Generic GET wrapper for Axcient x360Recover
# ---------------------------------------------------------------------
def axcient_get(endpoint, params=None):
    url = f"{AXCIENT_BASE_URL}{endpoint}"
    headers = {
        "accept": "application/json",
        "X-Api-Key": AXCIENT_API_KEY,
    }

    return api_get_json(url, headers, params)


# ---------------------------------------------------------------------
#  Pull all devices using pagination
# ---------------------------------------------------------------------
def fetch_all_axcient_devices(force=False):
    cached = read_cache(AXCIENT_CACHE_PATH_DEVICES)
    if cached and not force:
        log("Using cached Axcient data")
        return cached

    log("Fetching Axcient devices (paginated)...")

    all_devices = []
    offset = 0
    limit = AXCIENT_PAGE_SIZE

    while True:
        batch = axcient_get("/device", params={"limit": limit, "offset": offset})
        if batch is None:
            warn(f"Axcient: no data returned at offset {offset}")
            break

        if isinstance(batch, dict):
            # Unexpected form — usually list only
            batch = batch.get("devices", [])

        if not isinstance(batch, list):
            warn("Axcient returned non-list device payload")
            break

        if not batch:
            break

        all_devices.extend(batch)
        offset += limit

        if len(batch) < limit:
            break  # No more pages

    write_cache(AXCIENT_CACHE_PATH_DEVICES, all_devices)
    return all_devices


# ---------------------------------------------------------------------
#  Preflight validation
# ---------------------------------------------------------------------
def preflight_axcient():
    log("Preflight: Checking Axcient API...")

    resp = axcient_get("/device", params={"limit": 1, "offset": 0})
    if resp is None:
        warn("Axcient preflight FAILED (soft)")
        return False

    if isinstance(resp, list) and len(resp) > 0:
        log("Axcient preflight OK")
        return True

    warn("Axcient preflight FAILED (soft)")
    return False
