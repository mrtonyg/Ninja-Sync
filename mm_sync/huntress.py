"""
huntress.py
Version: 2.0.1
Author: Anthony George
"""

import requests
from requests.auth import HTTPBasicAuth
from mm_sync.utils import log, load_cache, save_cache
from mm_sync.config import ENDPOINTS, HUNTRESS_CACHE, CACHE_TTL
from mm_sync import secrets


BASE = ENDPOINTS["huntress"]["base"]


# -------------------------------------------------------------------------
# Raw GET wrapper
# -------------------------------------------------------------------------
def huntress_get(path, params=None, soft=False):
    url = f"{BASE}{path}"
    try:
        r = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(secrets.HUNTRESS_KEY, secrets.HUNTRESS_SECRET)
        )
        if not r.ok:
            if not soft:
                log(f"Huntress GET failed {url}: {r.status_code} {r.text}", "ERROR")
            return None
        return r.json()
    except Exception as ex:
        if not soft:
            log(f"Huntress exception: {ex}", "ERROR")
        return None


# -------------------------------------------------------------------------
# Preflight Check
# -------------------------------------------------------------------------
def preflight_huntress():
    test = huntress_get("/agents", {"page": 1}, soft=True)
    if test is None:
        log("Huntress preflight failed (soft)", "WARN")
        return False
    log("Huntress preflight OK")
    return True


# -------------------------------------------------------------------------
# Pull Agents + Organizations (cached)
# -------------------------------------------------------------------------
def pull_huntress():
    cached = load_cache(HUNTRESS_CACHE, CACHE_TTL["huntress"])
    if cached:
        log("Using cached Huntress data")
        return cached

    log("Fetching Huntress agents...")
    agents = []
    page = 1

    while True:
        batch = huntress_get("/agents", {"page": page})
        if not batch or "agents" not in batch:
            break
        agents.extend(batch["agents"])
        if len(batch["agents"]) < 100:
            break
        page += 1

    log("Fetching Huntress organizations...")
    orgs = {}
    page = 1
    while True:
        batch = huntress_get("/organizations", {"page": page})
        if not batch or "organizations" not in batch:
            break
        for o in batch["organizations"]:
            orgs[o["id"]] = o["name"]
        if len(batch["organizations"]) < 100:
            break
        page += 1

    data = {"agents": agents, "orgs": orgs}
    save_cache(HUNTRESS_CACHE, data)
    return data
