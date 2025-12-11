"""
Huntress API Client
Version: 2.0.7
Author: Anthony George

Implements:
 - Correct Base64 Basic Auth using public/private key pair
 - Paginated fetch for agents and organizations
 - Safe error handling
 - Soft-fail compatible behavior
"""

import base64
import requests
from typing import Dict, Any, List, Optional

from mm_sync.config import (
    HUNTRESS_BASE_URL,
    HUNTRESS_CACHE_PATH_AGENTS,
    HUNTRESS_CACHE_PATH_ORGS,
    CACHE_TTL_HUNTRESS,
)

from mm_sync.secrets import (
    HUNTRESS_PUBLIC_KEY,
    HUNTRESS_PRIVATE_KEY,
)

from mm_sync.utils import (
    log, warn, error,
    load_cache, save_cache,
)


# ----------------------------------------------------------------------
# AUTH HEADERS
# ----------------------------------------------------------------------

def huntress_headers() -> Dict[str, str]:
    """
    Generates Huntress Basic Auth header:
        Authorization: Basic base64(public:private)
    """
    raw = f"{HUNTRESS_PUBLIC_KEY}:{HUNTRESS_PRIVATE_KEY}"
    token = base64.b64encode(raw.encode()).decode()

    return {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
    }


# ----------------------------------------------------------------------
# RAW GET (with logging)
# ----------------------------------------------------------------------

def huntress_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Perform GET against Huntress API, returning JSON or None."""
    url = f"{HUNTRESS_BASE_URL}{endpoint}"

    try:
        resp = requests.get(url, headers=huntress_headers(), params=params)
    except Exception as ex:
        error(f"Huntress network error {url}: {ex}")
        return None

    if resp.status_code != 200:
        error(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
        return None

    try:
        return resp.json()
    except Exception as ex:
        error(f"Huntress response JSON decode failed {url}: {ex}")
        return None


# ----------------------------------------------------------------------
# PAGINATION HELPERS
# ----------------------------------------------------------------------

def fetch_paginated(endpoint: str) -> List[Dict[str, Any]]:
    """
    Fetches paginated Huntress lists (agents, organizations).
    Huntress uses:
        page=<n>
    """
    results = []
    page = 1

    while True:
        data = huntress_get(endpoint, params={"page": page})
        if not data:
            break

        items = data.get("data") or data.get("results") or data.get("agents") or data.get("organizations")
        if not items:
            break

        results.extend(items)

        # Huntress returns "next" field OR no indication when pages exhausted.
        meta = data.get("meta", {})
        if not meta:
            # fallback: stop if fewer than 100 items
            if len(items) < 100:
                break
        else:
            if not meta.get("next"):
                break

        page += 1

    return results


# ----------------------------------------------------------------------
# FETCH AGENTS & ORGS (WITH CACHING)
# ----------------------------------------------------------------------

def get_huntress_agents(force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
    """Loads Huntress agents with caching."""
    if not force_refresh:
        cached = load_cache(HUNTRESS_CACHE_PATH_AGENTS, CACHE_TTL_HUNTRESS)
        if cached:
            log("Using cached Huntress agents")
            return cached

    log("Fetching Huntress agents...")
    agents = fetch_paginated("/v1/agents")
    if agents:
        save_cache(HUNTRESS_CACHE_PATH_AGENTS, agents)
    return agents


def get_huntress_orgs(force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
    """Loads Huntress organizations with caching."""
    if not force_refresh:
        cached = load_cache(HUNTRESS_CACHE_PATH_ORGS, CACHE_TTL_HUNTRESS)
        if cached:
            log("Using cached Huntress organizations")
            return cached

    log("Fetching Huntress organizations...")
    orgs = fetch_paginated("/v1/organizations")
    if orgs:
        save_cache(HUNTRESS_CACHE_PATH_ORGS, orgs)
    return orgs


# ----------------------------------------------------------------------
# PREFLIGHT VALIDATION
# ----------------------------------------------------------------------

def huntress_preflight() -> bool:
    """
    Performs a single lightweight validation call.
    soft-fail OK: returns True/False
    """
    log("Running Huntress preflight check...")

    resp = huntress_get("/v1/agents", params={"page": 1})
    if resp is None:
        warn("Huntress preflight failed (soft)")
        return False

    log("Huntress preflight OK")
    return True
