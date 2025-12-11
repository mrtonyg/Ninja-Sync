# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import os
import json
import time
from .logger import info, warn

def load_cache(path, ttl):
    if not os.path.exists(path):
        return None

    age = time.time() - os.path.getmtime(path)
    if age > ttl:
        warn(f"Cache expired: {path}")
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        warn(f"Cache unreadable: {path}")
        return None

def write_cache(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def clear_cache(path):
    if os.path.exists(path):
        os.remove(path)
        info(f"Cleared cache: {path}")

def clear_cache_group(*paths):
    for p in paths:
        clear_cache(p)
