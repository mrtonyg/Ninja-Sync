# axcient.py
# Full Axcient x360Recover integration (paged), caching, HTML rendering.

import time
import requests
import os

from .secrets import AXCIENT_API_KEY
from .config import (
    AXCIENT_CACHE_DIR,
    CACHE_TTL_AXCIENT
)
from .utils import (
    log, log_error,
    json_load, json_save,
    safe_str, ic_status
)

# ------------------------------------------------------------
# Cache paths
# ------------------------------------------------------------
AX_DEVICES_CACHE_PATH = os.path.join(AXCIENT_CACHE_DIR, "devices.json")
AX_TS_CACHE_PATH      = os.path.join(AXCIENT_CACHE_DIR, "timestamp.json")

# ------------------------------------------------------------
# Low-level GET
# ------------------------------------------------------------
def axcient_get(path, params=None):
    url = f"https://axapi.axcient.com/x360recover{path}"
    headers = {
        "Accept": "application/json",
        "X-Api-Key": AXCIENT_API_KEY
    }
    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            log_error("Axcient API error", url, params, resp)
            return None
        return resp.json()
    except Exception as e:
        log_error("Axcient GET exception", url, params, exc=e)
        return None

# ------------------------------------------------------------
# Cache validity
# ------------------------------------------------------------
def axcient_cache_valid():
    ts = json_load(AX_TS_CACHE_PATH)
    if not ts:
        return False
    return (time.time() - ts.get("timestamp",0)) < CACHE_TTL_AXCIENT

# ------------------------------------------------------------
# Save cache
# ------------------------------------------------------------
def axcient_save_cache(devices):
    os.makedirs(AXCIENT_CACHE_DIR, exist_ok=True)
    json_save(AX_DEVICES_CACHE_PATH, devices)
    json_save(AX_TS_CACHE_PATH, {"timestamp": time.time()})

# ------------------------------------------------------------
# Load cache
# ------------------------------------------------------------
def axcient_load_cache():
    d = json_load(AX_DEVICES_CACHE_PATH)
    return d if d else None

# ------------------------------------------------------------
# Pull devices (paged)
# ------------------------------------------------------------
def pull_axcient(force_refresh=False):
    if not force_refresh and axcient_cache_valid():
        d = axcient_load_cache()
        if d:
            log("[INFO] Using cached Axcient devices")
            return d

    log("[INFO] Fetching Axcient devices (paginated)...")

    all_devices = []
    limit = 200
    offset = 0

    while True:
        params = {"limit": limit, "offset": offset}
        data = axcient_get("/device", params=params)

        if data is None:
            break

        # raw list OR wrapped dict
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
        time.sleep(0.15)

    axcient_save_cache(all_devices)
    return all_devices

# ------------------------------------------------------------
# HTML builder
# ------------------------------------------------------------
def html_axcient(d):
    name = safe_str(d.get("name"))
    agent_version = safe_str(d.get("agent_version"))
    latest_cloud_rp = safe_str(d.get("latest_cloud_rp"))

    chs = d.get("current_health_status") or {}
    health_status = safe_str(chs.get("status"))
    health_ts = safe_str(chs.get("timestamp"))

    av = d.get("latest_autoverify_details") or {}
    av_status = safe_str(av.get("status"))
    av_ts = safe_str(av.get("timestamp"))

    # Inline status
    status_line = f"{ic_status(health_status)} {health_status}"
    if health_ts not in ("", "Unknown"):
        status_line += f" ({health_ts})"

    # Inline AutoVerify
    av_line = f"{ic_status(av_status)} {av_status}"
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

