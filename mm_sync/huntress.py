"""
Huntress API
Author: Anthony George
Version: 2.0.5
"""

import requests
import datetime
from utils import log, warn, error, load_cache, save_cache, cache_valid, make_basic_auth
from secrets import HUNTRESS_PUBLIC_KEY, HUNTRESS_PRIVATE_KEY
from config import CACHE_PATH, CACHE_TTL_HUNTRESS, HUNTRESS_BASE_URL, FORCE_EXPIRE_HUNTRESS

CACHE_FILE = f"{CACHE_PATH}/huntress.json"

def huntress_get(endpoint, params=None):
    auth = make_basic_auth(HUNTRESS_PUBLIC_KEY, HUNTRESS_PRIVATE_KEY)
    headers = {"Authorization": f"Basic {auth}"}

    url = f"{HUNTRESS_BASE_URL}{endpoint}"
    resp = requests.get(url, headers=headers, params=params or {})

    if resp.status_code != 200:
        error(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
        return None

    return resp.json()

def pull_huntress():
    if FORCE_EXPIRE_HUNTRESS:
        cache = None
    else:
        cache = load_cache(CACHE_FILE)

    if cache_valid(cache, CACHE_TTL_HUNTRESS):
        log("Using cached Huntress data")
        return cache["agents"], cache["orgs"]

    log("Fetching Huntress agents...")
    agents = []
    page = 1
    while True:
        data = huntress_get("/agents", {"page": page})
        if not data or "agents" not in data:
            break
        agents.extend(data["agents"])
        if not data.get("pagination", {}).get("has_more"):
            break
        page += 1

    log("Fetching Huntress organizations...")
    orgs = {}
    page = 1
    while True:
        data = huntress_get("/organizations", {"page": page})
        if not data or "organizations" not in data:
            break
        for o in data["organizations"]:
            orgs[o["id"]] = o["name"]
        if not data.get("pagination", {}).get("has_more"):
            break
        page += 1

    save_cache(CACHE_FILE, {
        "_timestamp": datetime.datetime.utcnow().isoformat(),
        "agents": agents,
        "orgs": orgs
    })
    return agents, orgs

def preflight_huntress():
    test = huntress_get("/agents", {"page": 1})
    return test is not None
