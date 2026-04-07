"""
NinjaRMM API Integration
Version: 1.0.0
Purpose: OAuth authentication, device inventory retrieval, and custom field updates for NinjaRMM
Usage: Called by sync2Ninja.py to fetch devices and update huntressStatus/backupStatus fields
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com
"""
import time
import requests
import json
import os

from .config import NINJA_CACHE_DIR, CACHE_TTL_NINJA
from .secrets import (
    NINJA_BASE_URL,
    NINJA_OAUTH_CLIENT_ID,
    NINJA_OAUTH_CLIENT_SECRET
)
from .utils import log, log_error, strip_html


# OAuth token
_cached_token = None
_token_exp = 0


def ninja_token():
    global _cached_token, _token_exp

    if time.time() < _token_exp:
        return _cached_token

    url = f"{NINJA_BASE_URL}/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": NINJA_OAUTH_CLIENT_ID,
        "client_secret": NINJA_OAUTH_CLIENT_SECRET,
        "scope": "monitoring management control"
    }

    resp = requests.post(url, data=data)
    if resp.status_code != 200:
        log_error("OAuth token failure", url, data, resp)
        raise Exception("Ninja OAuth fail")

    js = resp.json()
    _cached_token = js["access_token"]
    _token_exp = time.time() + js.get("expires_in", 300) - 5
    log("[INFO] Obtained Ninja OAuth token")
    return _cached_token


def headers():
    return {
        "Authorization": f"Bearer {ninja_token()}",
        "Content-Type": "application/json"
    }


# Cache
DEV_FILE = os.path.join(NINJA_CACHE_DIR, "devices.json")
TS_FILE  = os.path.join(NINJA_CACHE_DIR, "timestamp.json")


def cache_valid():
    try:
        with open(TS_FILE, "r") as f:
            ts = json.load(f)["timestamp"]
        return (time.time() - ts) < CACHE_TTL_NINJA
    except:
        return False


def save_cache(devs):
    os.makedirs(NINJA_CACHE_DIR, exist_ok=True)
    with open(DEV_FILE, "w") as f:
        json.dump(devs, f, indent=4)
    with open(TS_FILE, "w") as f:
        json.dump({"timestamp": time.time()}, f)


def load_cache():
    try:
        with open(DEV_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def ninja_get_all_devices():
    if cache_valid():
        devs = load_cache()
        if devs:
            log("[INFO] Using cached Ninja devices")
            return devs

    log("[INFO] Fetching Ninja devices...")

    devices = []
    page = 1

    while True:
        url = f"{NINJA_BASE_URL}/v2/devices?page={page}&limit=500"
        resp = requests.get(url, headers=headers())

        if resp.status_code != 200:
            log_error("Failed fetching Ninja devices", url, None, resp)
            break

        batch = resp.json()
        if not batch:
            break

        devices.extend(batch)

        if len(batch) < 500:
            break

        page += 1

    save_cache(devices)
    return devices


def ninja_update_field(device_id, field_name, html, src_name, ninja_name):
    url = f"{NINJA_BASE_URL}/v2/device/{device_id}/custom-fields"

    payload = {
        field_name: {
            "text": strip_html(html),
            "html": html
        }
    }

    resp = requests.patch(url, headers=headers(), json=payload)
    if resp.status_code not in (200, 204):
        log_error(f"Failed updating {field_name}",
                  url, payload, resp)
        return False

    log(f"[OK] Updated {field_name} → {src_name} → NinjaOne: {ninja_name} ({device_id})")
    return True
