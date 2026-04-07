"""
Axcient x360Recover API Integration
Version: 1.0.0
Purpose: Pull device/backup data from Axcient x360Recover API, cache results, generate HTML status
Usage: Called by sync2Ninja.py to retrieve backup protection status
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com
"""
import requests
import json
import os
import time

from .secrets import AXCIENT_API_KEY, AXCIENT_BASE_URL
from .config import AXCIENT_CACHE_DIR, CACHE_TTL_AXCIENT
from .utils import log, log_error


# Cache paths
DEVICES_FILE = os.path.join(AXCIENT_CACHE_DIR, "devices.json")
TS_FILE      = os.path.join(AXCIENT_CACHE_DIR, "timestamp.json")


def cache_valid():
    try:
        with open(TS_FILE, "r") as f:
            ts = json.load(f)["timestamp"]
        return (time.time() - ts) < CACHE_TTL_AXCIENT
    except:
        return False


def load_cache():
    try:
        with open(DEVICES_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def save_cache(devices):
    os.makedirs(AXCIENT_CACHE_DIR, exist_ok=True)
    with open(DEVICES_FILE, "w") as f:
        json.dump(devices, f, indent=4)
    with open(TS_FILE, "w") as f:
        json.dump({"timestamp": time.time()}, f)


def ax_get(path, params=None):
    url = f"{AXCIENT_BASE_URL}{path}"
    headers = {
        "x-api-key": AXCIENT_API_KEY,
        "Accept": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            log_error("Axcient API error", url, params, resp)
            raise Exception("Axcient failure")
        return resp.json()
    except Exception as e:
        log_error(f"Axcient exception {e}", url, params)
        raise


def pull_axcient():
    if cache_valid():
        devices = load_cache()
        if devices:
            log("[INFO] Using cached Axcient data")
            return devices

    log("[INFO] Fetching Axcient devices...")

    all_devices = []
    limit = 200
    offset = 0

    while True:
        params = {"limit": limit, "offset": offset}
        data = ax_get("/device", params)

        # Normalize
        if isinstance(data, list):
            batch = data
        elif isinstance(data, dict) and "devices" in data:
            batch = data["devices"]
        else:
            batch = []

        if not batch:
            break

        all_devices.extend(batch)

        if len(batch) < limit:
            break

        offset += limit
        time.sleep(0.1)

    save_cache(all_devices)
    return all_devices

def html_axcient(d):
    safe = lambda x: x if x else "Unknown"

    def ic(v):
        if not v:
            return "⚪"
        v = v.lower()
        if "success" in v or "normal" in v or "healthy" in v:
            return "🟢"
        if "warn" in v or "warning" in v:
            return "🟡"
        return "🔴"

    # Core fields
    name = safe(d.get("name"))
    agent_version = safe(d.get("agent_version"))
    latest_cloud_rp = safe(d.get("latest_cloud_rp"))

    # Current health
    chs = d.get("current_health_status") or {}
    health_status = safe(chs.get("status"))
    health_ts = safe(chs.get("timestamp"))

    # AutoVerify
    av = d.get("latest_autoverify_details") or {}
    av_status = safe(av.get("status"))
    av_ts = safe(av.get("timestamp"))

    # Inline status
    status_line = f"{ic(health_status)} {health_status}"
    if health_ts not in ("", "Unknown"):
        status_line += f" ({health_ts})"

    # Inline AutoVerify
    av_line = f"{ic(av_status)} {av_status}"
    if av_ts not in ("", "Unknown"):
        av_line += f" ({av_ts})"

    return f"""
<p><b><u>Axcient Backup</u></b></p>

<p><b>Name:</b> {name}</p>
<p><b>Agent Version:</b> {agent_version}</p>
<p><b>Latest Cloud RP:</b> {latest_cloud_rp}</p>

<p><b>Current Status:</b> {status_line}</p>
<p><b>AutoVerify:</b> {av_line}</p>
""".strip()
