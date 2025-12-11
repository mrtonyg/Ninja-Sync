"""
axcient.py
Version: 2.0.1
Author: Anthony George
"""

from mm_sync.utils import log, load_cache, save_cache, http_get
from mm_sync.config import ENDPOINTS, AXCIENT_CACHE, CACHE_TTL
from mm_sync import secrets


BASE = ENDPOINTS["axcient"]["base"]


# -------------------------------------------------------------------------
# Preflight Check
# -------------------------------------------------------------------------
def preflight_axcient():
    url = f"{BASE}{ENDPOINTS['axcient']['devices']}"
    r = http_get(url, headers={"X-Api-Key": secrets.AXCIENT_API_KEY}, soft=True)
    if r is None:
        log("Axcient preflight failed (soft)", "WARN")
        return False
    log("Axcient preflight OK")
    return True


# -------------------------------------------------------------------------
# Paginated fetch
# -------------------------------------------------------------------------
def pull_axcient():
    cached = load_cache(AXCIENT_CACHE, CACHE_TTL["axcient"])
    if cached:
        log("Using cached Axcient data")
        return cached

    log("Fetching Axcient devices (paginated)...")

    devices = []
    limit = 100
    offset = 0

    while True:
        url = f"{BASE}{ENDPOINTS['axcient']['devices']}"
        r = http_get(url, headers={"X-Api-Key": secrets.AXCIENT_API_KEY},
                     params={"limit": limit, "offset": offset})
        if r is None:
            break

        batch = r.json()
        if not isinstance(batch, list):
            break

        devices.extend(batch)
        if len(batch) < limit:
            break

        offset += limit

    save_cache(AXCIENT_CACHE, devices)
    return devices
