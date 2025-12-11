"""
Utility functions
Author: Anthony George
Version: 2.0.5
"""

import os
import json
import base64
import datetime
import re

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{now()}] [INFO] {msg}")

def warn(msg):
    print(f"[{now()}] [WARN] {msg}")

def error(msg):
    print(f"[{now()}] [ERROR] {msg}")

# -----------------------------------
# Strip HTML for Ninja "text" version
# -----------------------------------
def strip_html(html: str) -> str:
    return re.sub(r"<[^>]*>", "", html)

# -----------------------------------
# Simple JSON cache load/save
# -----------------------------------
def load_cache(path):
    if not os.path.exists(path):
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

# -----------------------------------
# Check TTL expiration
# -----------------------------------
def cache_valid(cache, ttl):
    if cache is None:
        return False
    ts = cache.get("_timestamp")
    if ts is None:
        return False
    age = (datetime.datetime.utcnow() - datetime.datetime.fromisoformat(ts)).total_seconds()
    return age < ttl

# -----------------------------------
# Create Basic Auth header (Huntress)
# -----------------------------------
def make_basic_auth(user, password):
    raw = f"{user}:{password}".encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")
