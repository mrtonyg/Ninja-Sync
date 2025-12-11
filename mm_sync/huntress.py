"""
huntress.py
Version: 2.0.3
Author: Anthony George

Implements correct Huntress API authentication per:
https://api.huntress.io/docs

Authentication Format:
    Authorization: Basic base64("<public_key>:<private_key>")
"""

import base64
import requests
from mm_sync.utils import log, load_cache, save_cache
from mm_sync.config import ENDPOINTS, HUNTRESS_CACHE, CACHE_TTL
from mm_sync import secrets


BASE = ENDPOINTS["huntress"]["base"]


# -------------------------------------------------------------------------
# Correct Huntress Authentication Header
# -------------------------------------------------------------------------
def huntress_headers():
    token = f"{secrets.HUNTRESS_KEY}:{secrets.HUNTRESS_SECRET}"
    encoded = base64.b64encode(token.encode()).decode()

    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json",
    }


# -------------------------------------------------------------------------
# API Wrapper
# -------------------------------------------------------------------------
def huntress_get(path, params=None, soft=False):
    url = f"{BASE}{path}"

    try:
        r = requests.get(url, headers=huntress_headers(), params=params, timeout=30)

        if not r.ok:
            if not soft:
                log(f"Huntress GET failed {url}: {r.status_code} {r.text}", "ERROR")
            return None

        return r.json()

    except Exception as ex:
        if not soft:
            log(f"Huntress GET exception: {ex}", "ERROR")
        return None


# -------------------------------------------------------------------------
# Preflight Check
# -------------------------------------------------------------------------
def preflight_huntress():
    test = huntress_get("/agents", {"limit": 1}, soft=True)
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
        data = huntress_get("/agents", {"page": page})
        if not data or "agents" not in data:
            break

        agents.extend(data["agents"])

        if len(data["agents"]) < 100:
            break

        page += 1

    log("Fetching Huntress organizations...")

    orgs = {}
    page = 1

    while True:
        data = huntress_get("/organizations", {"page": page})
        if not data or "organizations" not in data:
            break

        for org in data["organizations"]:
            orgs[org["id"]] = org["name"]

        if len(data["organizations"]) < 100:
            break

        page += 1

    merged = {"agents": agents, "orgs": orgs}
    save_cache(HUNTRESS_CACHE, merged)
    return merged
