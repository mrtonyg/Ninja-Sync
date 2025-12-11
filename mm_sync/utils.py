"""
Utility functions
Author: Anthony George
Version: 2.0.6
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

# ---------------------------
# Strip HTML → for Ninja WYSIWYG 'text' field
# ---------------------------
def strip_html(html):
    return re.sub(r"<[^>]*>", "", html)

# ---------------------------
# Cache management
# ---------------------------
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

def cache_valid(cache, ttl):
    if cache is None:
        return False
    ts = cache.get("_timestamp")
    if not ts:
        return False
    age = (datetime.datetime.utcnow() - datetime.datetime.fromisoformat(ts)).total_seconds()
    return age < ttl

# ---------------------------
# Huntress Basic Auth
# ---------------------------
def make_basic_auth(pub, priv):
    raw = f"{pub}:{priv}".encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")
