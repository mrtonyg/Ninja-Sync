"""
Huntress API
Author: Anthony George
Version: 2.0.7
"""

import requests
import datetime
import base64

from mm_sync.utils import log, warn, error, load_cache, save_cache, cache_valid
from mm_sync.secrets import HUNTRESS_KEY, HUNTRESS_SECRET
from mm_sync.config import CACHE_PATH, CACHE_TTL_HUNTRESS, HUNTRESS_BASE_URL, FORCE_EXPIRE_HUNTRESS

CACHE_FILE = f"{CACHE_PATH}/huntress.json"

def make_huntress_auth():
    """Return proper Basic Auth header value for Huntress."""
    raw = f"{HUNTRESS_KEY}:{HUNTRESS_SECRET}".encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")

def huntress_get(endpoint, params=None):
    """Perform authenticated Huntress GET request."""
    auth = make_huntress_auth()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json"
    }
    url = f"{HUNTRESS_BASE_URL}{endpoint}"

    resp = requests.get(url, headers=headers, params=params or {})

    if resp.status_code != 200:
        error(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
        return None

    return resp.json()

def pull_huntress():
    """Load agents + orgs from cache or API."""
    cache = None if FORCE_EXPIRE_HUNTRESS else load_cache(CACHE_FILE)

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

        for org in data["organizations"]:
            orgs[org["id"]] = org["name"]

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
    """Lightweight validation of Huntress creds."""
    test = huntress_get("/agents", {"page": 1})
    return test is not None
