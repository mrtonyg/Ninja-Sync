"""
=====================================================================
  ninja_sync/api/huntress_api.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Huntress API Integration
=====================================================================

Implements:
  - build_huntress_auth()
  - huntress_get(endpoint, params=None)
  - fetch_all_agents()
  - fetch_all_orgs()
  - preflight_huntress()
"""

import base64
from ..core.logging import log, warn, error
from ..core.config import (
    HUNTRESS_BASE_URL,
    HUNTRESS_CACHE_PATH_AGENTS,
    HUNTRESS_CACHE_PATH_ORGS,
)
from ..core.secrets import (
    HUNTRESS_PUBLIC_KEY,
    HUNTRESS_PRIVATE_KEY,
)
from .base_api import api_get_json
from ..core.cache import load_cache, save_cache


# ---------------------------------------------------------------------
#  Build Authorization header for Huntress Basic Auth
# ---------------------------------------------------------------------
def build_huntress_auth():
    keypair = f"{HUNTRESS_PUBLIC_KEY}:{HUNTRESS_PRIVATE_KEY}"
    encoded = base64.b64encode(keypair.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


# ---------------------------------------------------------------------
#  Generic Huntress GET wrapper
# ---------------------------------------------------------------------
def huntress_get(endpoint, params=None):
    url = f"{HUNTRESS_BASE_URL}{endpoint}"
    headers = build_huntress_auth()
    data = api_get_json(url, headers, params)

    if data is None:
        error(f"Huntress GET failed {url}: {data}")
        return None

    return data


# ---------------------------------------------------------------------
#  Pull agents (with pagination)
# ---------------------------------------------------------------------
def fetch_all_agents(force=False):
    cached = load_cache(HUNTRESS_CACHE_PATH_AGENTS)
    if cached and not force:
        log("Using cached Huntress agents")
        return cached

    log("Fetching Huntress agents...")

    agents = []
    page = 1
    while True:
        resp = huntress_get("/api/v1/agents", params={"page": page})
        if not resp or "agents" not in resp:
            break

        agents.extend(resp["agents"])
        if not resp.get("has_more"):
            break
        page += 1

    save_cache(HUNTRESS_CACHE_PATH_AGENTS, agents)
    return agents


# ---------------------------------------------------------------------
#  Pull organizations (with pagination)
# ---------------------------------------------------------------------
def fetch_all_orgs(force=False):
    cached = load_cache(HUNTRESS_CACHE_PATH_ORGS)
    if cached and not force:
        log("Using cached Huntress organizations")
        return cached

    log("Fetching Huntress organizations...")

    orgs = []
    page = 1
    while True:
        resp = huntress_get("/api/v1/organizations", params={"page": page})
        if not resp or "organizations" not in resp:
            break

        orgs.extend(resp["organizations"])
        if not resp.get("has_more"):
            break
        page += 1

    save_cache(HUNTRESS_CACHE_PATH_ORGS, orgs)
    return orgs


# ---------------------------------------------------------------------
#  Preflight validation
# ---------------------------------------------------------------------
def preflight_huntress():
    log("Preflight: Checking Huntress API...")

    resp = huntress_get("/api/v1/agents", params={"page": 1})
    if resp is None or "agents" not in resp:
        warn("Huntress preflight FAILED (soft)")
        return False

    log("Huntress preflight OK")
    return True
