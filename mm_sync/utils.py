"""
utils.py
Version: 2.0.1
Author: Anthony George
"""

import os
import json
import time
import requests


# -------------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------------
def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


# -------------------------------------------------------------------------
# Cache Handling
# -------------------------------------------------------------------------
def load_cache(path, max_age):
    if not os.path.exists(path):
        return None

    age = time.time() - os.path.getmtime(path)
    if age > max_age:
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None


def save_cache(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# -------------------------------------------------------------------------
# HTTP helper with soft-fail preflight
# -------------------------------------------------------------------------
def http_get(url, headers=None, params=None, soft=False):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if not r.ok:
            if not soft:
                log(f"HTTP GET failed {r.status_code}: {r.text}", "ERROR")
            return (None if soft else r)
        return r
    except Exception as ex:
        if not soft:
            log(f"HTTP GET Exception: {ex}", "ERROR")
        return None
