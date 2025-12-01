# huntress.py
# Full Huntress integration: agents, org lookup, caching, HTML rendering.

import time
import requests
from .secrets import HUNTRESS_KEY, HUNTRESS_SECRET
from .config import (
    HUNTRESS_CACHE_DIR,
    CACHE_TTL_HUNTRESS
)
from .utils import (
    log, log_error,
    json_load, json_save,
    safe_str, ic_status
)
import os

# ------------------------------------------------------------
# Internal paths
# ------------------------------------------------------------
AGENTS_CACHE_PATH = os.path.join(HUNTRESS_CACHE_DIR, "agents.json")
ORGS_CACHE_PATH   = os.path.join(HUNTRESS_CACHE_DIR, "orgs.json")
TS_CACHE_PATH     = os.path.join(HUNTRESS_CACHE_DIR, "timestamp.json")

# ------------------------------------------------------------
# Low-level Huntress GET helper
# ------------------------------------------------------------
def huntress_get(path, params=None):
    url = f"https://api.huntress.io/api/v1{path}"
    headers = {
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, params=params, auth=(HUNTRESS_KEY, HUNTRESS_SECRET))
        if resp.status_code != 200:
            log_error("Huntress API error", url, params, resp)
            return None
        return resp.json()
    except Exception as e:
        log_error("Huntress GET exception", url, params, exc=e)
        return None

# ------------------------------------------------------------
# Cache validation
# ------------------------------------------------------------
def huntress_cache_valid():
    ts = json_load(TS_CACHE_PATH)
    if not ts:
        return False
    return (time.time() - ts.get("timestamp",0)) < CACHE_TTL_HUNTRESS

# ------------------------------------------------------------
# Save cache
# ------------------------------------------------------------
def save_cache(agents, orgs):
    os.makedirs(HUNTRESS_CACHE_DIR, exist_ok=True)
    json_save(AGENTS_CACHE_PATH, agents)
    json_save(ORGS_CACHE_PATH, orgs)
    json_save(TS_CACHE_PATH, {"timestamp": time.time()})

# ------------------------------------------------------------
# Load cache
# ------------------------------------------------------------
def load_cache():
    agents = json_load(AGENTS_CACHE_PATH)
    orgs = json_load(ORGS_CACHE_PATH)
    if agents and orgs:
        return agents, orgs
    return None, None

# ------------------------------------------------------------
# Pull organizations (paged)
# ------------------------------------------------------------
def pull_orgs():
    orgs = []
    page = 1
    while True:
        data = huntress_get("/organizations", {"page": page})
        if not data or "data" not in data:
            break
        batch = data["data"]
        if not batch:
            break
        orgs.extend(batch)
        if "next_page" in data and not data["next_page"]:
            break
        if len(batch) < 25:
            break
        page += 1
    return orgs

# ------------------------------------------------------------
# Pull agents (paged)
# ------------------------------------------------------------
def pull_agents():
    agents = []
    page = 1
    while True:
        data = huntress_get("/agents", {"page": page})
        if not data or "data" not in data:
            break
        batch = data["data"]
        if not batch:
            break
        agents.extend(batch)
        if len(batch) < 25:
            break
        page += 1
    return agents

# ------------------------------------------------------------
# Public function to pull Huntress data
# ------------------------------------------------------------
def pull_huntress(force_refresh=False):
    if not force_refresh and huntress_cache_valid():
        a, o = load_cache()
        if a and o:
            log("[INFO] Using cached Huntress data")
            return a, o

    log("[INFO] Fetching Huntress agents...")
    agents = pull_agents()

    log("[INFO] Fetching Huntress organizations...")
    orgs = pull_orgs()

    save_cache(agents, orgs)
    return agents, orgs

# ------------------------------------------------------------
# Enrich: map org_id -> org_name
# ------------------------------------------------------------
def enrich_huntress(agents, orgs):
    org_map = {o["id"]: o["name"] for o in orgs if "id" in o}
    for a in agents:
        org_id = a.get("organization_id")
        a["organization_name"] = org_map.get(org_id, "Unknown")
    return agents

# ------------------------------------------------------------
# HTML builder for Ninja custom field (Huntress)
# ------------------------------------------------------------
def html_huntress(a):
    name = safe_str(a.get("hostname"))
    org  = safe_str(a.get("organization_name"))
    sn   = safe_str(a.get("serial_number"))
    os   = safe_str(a.get("os"))
    plat = safe_str(a.get("platform"))
    ip_i = safe_str(a.get("ipv4_address"))
    ip_e = safe_str(a.get("external_ip"))
    cb   = safe_str(a.get("last_callback_at"))
    sv   = safe_str(a.get("last_survey_at"))
    ver  = safe_str(a.get("version"))
    edr  = safe_str(a.get("edr_version"))
    upd  = safe_str(a.get("updated_at"))

    df_st = safe_str(a.get("defender_status"))
    df_ss = safe_str(a.get("defender_substatus"))
    df_ps = safe_str(a.get("defender_policy_status"))
    fw_st = safe_str(a.get("firewall_status"))

    return f"""
<p><b><u>Huntress Status</u></b></p>

<p><b>Device Name:</b> {name}</p>
<p><b>Organization:</b> {org}</p>
<p><b>Serial Number:</b> {sn}</p>
<p><b>Operating System:</b> {os}</p>
<p><b>Platform:</b> {plat}</p>
<p><b>Internal IP:</b> {ip_i}</p>
<p><b>External IP:</b> {ip_e}</p>

<p><b>Last Callback:</b> {cb}</p>
<p><b>Last Survey:</b> {sv}</p>
<p><b>Updated At:</b> {upd}</p>

<p><b>Agent Version:</b> {ver}</p>
<p><b>EDR Version:</b> {edr}</p>

<p><b>Defender Status:</b> {ic_status(df_st)} {df_st}</p>
<p><b>Substatus:</b> {ic_status(df_ss)} {df_ss}</p>
<p><b>Policy:</b> {ic_status(df_ps)} {df_ps}</p>
<p><b>Firewall:</b> {ic_status(fw_st)} {fw_st}</p>
""".strip()

