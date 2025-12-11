"""
=====================================================================
  ninja_sync/api/base_api.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Base API Helpers
=====================================================================

Provides:
  - api_get_json(url, headers, params=None)
  - api_post_json(url, headers, payload)
  - api_patch_json(url, headers, payload)
"""

import json
import time
import requests
from ..core.logging import log, error


# -----------------------------------------------------------
# Shared JSON GET wrapper with error reporting
# -----------------------------------------------------------
def api_get_json(url, headers, params=None):
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    except Exception as exc:
        error(f"GET EXCEPTION {url}: {exc}")
        return None

    if resp.status_code not in (200, 201):
        error(f"GET FAILED {url} [{resp.status_code}]: {resp.text}")
        return None

    try:
        return resp.json()
    except json.JSONDecodeError:
        error(f"GET JSON PARSE FAILED {url}")
        return None


# -----------------------------------------------------------
# POST wrapper
# -----------------------------------------------------------
def api_post_json(url, headers, payload):
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
    except Exception as exc:
        error(f"POST EXCEPTION {url}: {exc}")
        return None

    if resp.status_code not in (200, 201):
        error(f"POST FAILED {url} [{resp.status_code}]: {resp.text}")
        return None

    try:
        return resp.json()
    except json.JSONDecodeError:
        error(f"POST JSON PARSE FAILED {url}")
        return None


# -----------------------------------------------------------
# PATCH wrapper
# -----------------------------------------------------------
def api_patch_json(url, headers, payload):
    try:
        resp = requests.patch(url, headers=headers, json=payload, timeout=30)
    except Exception as exc:
        error(f"PATCH EXCEPTION {url}: {exc}")
        return False

    if resp.status_code not in (200, 204):
        error(f"PATCH FAILED {url} [{resp.status_code}]: {resp.text}")
        return False

    return True
