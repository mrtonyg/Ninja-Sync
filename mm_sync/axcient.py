"""
Axcient API
Author: Anthony George
Version: 2.0.6
"""

import requests
import datetime

from mm_sync.utils import log, warn, error, load_cache, save_cache, cache_valid
from mm_sync.secrets import AXCIENT_API_KEY
from mm_sync.config import AXCIENT_BASE_URL, CACHE_PATH, CACHE_TTL_AXCIENT, FORCE_EXPIRE_AXCIENT

CACHE_FILE = f"{CACHE_PATH}/axcient.json"

def axcient_get(params):
    headers = {"X-Api-Key": AXCIENT_API_KEY}
    url = f"{AXCIENT_BASE_URL}/device"
    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        error(f"Axcient GET failed: {resp.status_code} {resp.text}")
        return None

    return resp.json()

def pull_axcient():
    cache = None if FORCE_EXPIRE_AXCIENT else load_cache(CACHE_FILE)

    if cache_valid(cache, CACHE_TTL_AXCIENT):
        log("Using cached Axcient data")
        return cache["devices"]

    log("Fetching Axcient devices (paginated)...")

    devices = []
    offset = 0
    limit = 50

    while True:
        data = axcient_get({"limit": limit, "offset": offset})
        if not isinstance(data, list):
            break

        devices.extend(data)

        if len(data) < limit:
            break

        offset += limit

    save_cache(CACHE_FILE, {
        "_timestamp": datetime.datetime.utcnow().isoformat(),
        "devices": devices
    })

    return devices

def preflight_axcient():
    test = axcient_get({"limit": 1, "offset": 0})
    return isinstance(test, list)
