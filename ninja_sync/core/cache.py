"""
=====================================================================
  ninja_sync/core/cache.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Unified Cache Engine
=====================================================================

Supports:
  - read_cache(path, ttl)
  - write_cache(path, data)
  - clear_cache(path)
  - clear_cache_group(group)

Groups are defined in config.CACHE_GROUPS:
  huntress, ninja, axcient, all
"""

import json
import os
import time

from ninja_sync.core.logger import log, warn, error
from ninja_sync.core.config import CACHE_GROUPS


# -------------------------------------------------------------------
# Load cache (returns None if expired or missing)
# -------------------------------------------------------------------
def read_cache(path: str, ttl: int):
    try:
        if not os.path.isfile(path):
            return None

        age = time.time() - os.path.getmtime(path)
        if age > ttl:
            warn(f"[CACHE] Cache expired: {path}")
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        log(f"[CACHE] Loaded cache: {path}")
        return data

    except Exception as exc:
        warn(f"[CACHE] Failed reading {path}: {exc}")
        return None


# -------------------------------------------------------------------
# Write cache
# -------------------------------------------------------------------
def write_cache(path: str, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        log(f"[CACHE] Updated cache: {path}")
        return True
    except Exception as exc:
        error(f"[CACHE] Failed writing {path}: {exc}")
        return False


# -------------------------------------------------------------------
# Clear single cache file
# -------------------------------------------------------------------
def clear_cache(path: str):
    try:
        if os.path.isfile(path):
            os.remove(path)
            log(f"[CACHE] Cleared: {path}")
        else:
            warn(f"[CACHE] No cache to clear: {path}")
    except Exception as exc:
        error(f"[CACHE] Could not clear {path}: {exc}")


# -------------------------------------------------------------------
# Clear group of cache files
# -------------------------------------------------------------------
def clear_cache_group(group: str):
    paths = CACHE_GROUPS.get(group)
    if not paths:
        error(f"[CACHE] Unknown cache group: {group}")
        return False

    log(f"[CACHE] Clearing cache group: {group}")
    for path in paths:
        clear_cache(path)
    return True
