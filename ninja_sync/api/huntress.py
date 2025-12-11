"""
=====================================================================
  ninja_sync/api/huntress.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Huntress API (v1)
=====================================================================

Implements:
  - huntress_get_agents(force=False)
  - huntress_get_orgs(force=False)
  - preflight_huntress()
"""

import base64
import requests

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
from ninja_sync.core.cache import read_cache, write_cache, clear_cache, clear_cache_group


# ===============================================================
#  Build Authorization Header
# ===============================================================

def _auth_header():
    """
    Huntress requires:
        Authorization: Basic <base64(pub:priv)>
    """

    token = f"{HUNTRESS_PUBLIC_KEY}:{HUNTRESS_PRIVATE_KEY}"
    encoded = base64.b64encode(token.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


# ===============================================================
#  GET with pagination
# ===============================================================

def _huntress_get(url, params=None):
    resp = requests.get(url, headers=_auth_header(), params=params or {})
    if resp.status_code != 200:
        error("Huntress GET failed", url, params, resp)
        return None
    return resp.json()


def huntress_get_agents(force=False):
    cached = read_cache(HUNTRESS_CACHE_PATH_AGENTS)
    if cached and not force:
        log("Using cached Huntress agents")
        return cached

    url = f"{HUNTRESS_BASE_URL}/agents"
    agents = []
    page = 1

    while True:
        data = _huntress_get(url, {"page": page})
        if not data:
            break

        part = data.get("agents", [])
        agents.extend(part)

        if not data.get("next_page"):
            break
        page += 1

    write_cache(HUNTRESS_CACHE_PATH_AGENTS, agents)
    return agents


def huntress_get_orgs(force=False):
    cached = read_cache(HUNTRESS_CACHE_PATH_ORGS)
    if cached and not force:
        log("Using cached Huntress organizations")
        return cached

    url = f"{HUNTRESS_BASE_URL}/organizations"
    orgs = []
    page = 1

    while True:
        data = _huntress_get(url, {"page": page})
        if not data:
            break

        part = data.get("organizations", [])
        orgs.extend(part)

        if not data.get("next_page"):
            break
        page += 1

    write_cache(HUNTRESS_CACHE_PATH_ORGS, orgs)
    return orgs


# ===============================================================
#  Preflight
# ===============================================================

def preflight_huntress():
    log("Preflight: Checking Huntress API...")

    url = f"{HUNTRESS_BASE_URL}/agents"
    resp = requests.get(url, headers=_auth_header(), params={"page": 1})

    if resp.status_code == 200:
        log("Huntress preflight OK")
        return True

    warn("Huntress preflight FAILED (soft)")
    warn(f"HTTP {resp.status_code}: {resp.text}")
    return False
