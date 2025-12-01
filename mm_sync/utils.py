# utils.py
# Shared logging, cache handling, and helper utilities.

import os
import json
import time
from datetime import datetime
from .config import (
    LOG_PATH,
    HUNTRESS_CACHE_DIR,
    AXCIENT_CACHE_DIR,
    NINJA_CACHE_DIR
)

# ------------------------------------------------------------
# Logging utilities
# ------------------------------------------------------------
def log(msg):
    ts = datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def log_error(msg, url=None, params=None, resp=None, exc=None):
    log("[ERROR] " + msg)
    if url:
        log(f"  URL: {url}")
    if params:
        log(f"  Params: {params}")
    if resp is not None:
        try:
            log(f"  HTTP Status: {resp.status_code}")
            log(f"  Response: {resp.text}")
        except Exception:
            pass
    if exc:
        log(f"  Exception: {repr(exc)}")

# ------------------------------------------------------------
# JSON utilities
# ------------------------------------------------------------
def json_save(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_error(f"Failed saving JSON to {path}", exc=e)

def json_load(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

# ------------------------------------------------------------
# Cache clearing
# ------------------------------------------------------------
def clear_cache_dir(path):
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except:
                    pass
        try:
            os.rmdir(path)
        except:
            pass
        log(f"[CACHE] Cleared: {path}")
    else:
        log(f"[CACHE] Not found: {path}")

def clear_huntress_cache():
    clear_cache_dir(HUNTRESS_CACHE_DIR)

def clear_axcient_cache():
    clear_cache_dir(AXCIENT_CACHE_DIR)

def clear_ninja_cache():
    clear_cache_dir(NINJA_CACHE_DIR)

def clear_all_caches():
    log("[CACHE] Clearing ALL caches...")
    clear_huntress_cache()
    clear_axcient_cache()
    clear_ninja_cache()
    log("[CACHE] All caches cleared.")

# ------------------------------------------------------------
# Formatting helpers
# ------------------------------------------------------------
def safe_str(value):
    return value if value not in (None, "", []) else "Unknown"

def ic_status(v):
    if not v:
        return "⚪"
    v=v.lower()
    if "success" in v or "normal" in v or "healthy" in v or "protected" in v or "compliant" in v:
        return "🟢"
    if "warn" in v or "warning" in v:
        return "🟡"
    return "🔴"

