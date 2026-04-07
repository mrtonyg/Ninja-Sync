"""
Huntress API Integration
Version: 1.0.0
Purpose: Pull agent and organization data from Huntress API, cache results, generate HTML status
Usage: Called by sync2Ninja.py to retrieve Huntress security monitoring data
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com
"""
import requests
import json
import time
import os

from .secrets import HUNTRESS_API_KEY, HUNTRESS_API_SECRET
from .config import HUNTRESS_CACHE_DIR, CACHE_TTL_HUNTRESS
from .utils import log, log_error


# Cache paths
AGENTS_FILE = os.path.join(HUNTRESS_CACHE_DIR, "agents.json")
ORGS_FILE   = os.path.join(HUNTRESS_CACHE_DIR, "orgs.json")
TS_FILE     = os.path.join(HUNTRESS_CACHE_DIR, "timestamp.json")


def cache_valid():
    try:
        with open(TS_FILE, "r") as f:
            ts = json.load(f)["timestamp"]
        return (time.time() - ts) < CACHE_TTL_HUNTRESS
    except:
        return False


def load_cache():
    try:
        with open(AGENTS_FILE, "r") as f:
            agents = json.load(f)
        with open(ORGS_FILE, "r") as f:
            orgs = json.load(f)
        return agents, orgs
    except:
        return None, None


def save_cache(agents, orgs):
    os.makedirs(HUNTRESS_CACHE_DIR, exist_ok=True)
    with open(AGENTS_FILE, "w") as f:
        json.dump(agents, f, indent=4)
    with open(ORGS_FILE, "w") as f:
        json.dump(orgs, f, indent=4)
    with open(TS_FILE, "w") as f:
        json.dump({"timestamp": time.time()}, f)


def h_get(path, params=None):
    url = f"https://api.huntress.io/v1{path}"
    try:
        resp = requests.get(url, params=params, auth=(HUNTRESS_API_KEY, HUNTRESS_API_SECRET))
        if resp.status_code != 200:
            log_error("Huntress API error", url, params, resp)
            raise Exception("Huntress fail")
        return resp.json()
    except Exception as e:
        log_error(f"Huntress exception: {e}", url, params)
        raise


def pull_huntress():
    if cache_valid():
        agents, orgs = load_cache()
        if agents and orgs:
            log("[INFO] Using cached Huntress data")
            return agents, orgs

    # Fetch orgs
    log("[INFO] Fetching Huntress orgs...")
    orgs = []
    page = 1
    while True:
        data = h_get("/organizations", {"page": page, "limit": 500})
        batch = data.get("organizations", [])
        if not batch:
            break
        orgs.extend(batch)
        if len(batch) < 500:
            break
        page += 1

    # Fetch agents
    log("[INFO] Fetching Huntress agents...")
    agents = []
    page = 1
    while True:
        data = h_get("/agents", {"page": page, "limit": 500})
        batch = data.get("agents", [])
        if not batch:
            break
        agents.extend(batch)
        if len(batch) < 500:
            break
        page += 1

    save_cache(agents, orgs)
    return agents, orgs


def enrich_huntress(agents, orgs):
    org_map = {o["id"]: o["name"] for o in orgs}
    for a in agents:
        a["organization_name"] = org_map.get(a.get("organization_id"), "Unknown")
    return agents


def html_huntress(a):
    safe = lambda x: x if x else "Unknown"

    def ic(v):
        if not v: return "⚪"
        v = v.lower()
        if any(k in v for k in ["protected", "enabled", "compliant", "up to date"]):
            return "🟢"
        if "warning" in v:
            return "🟡"
        return "🔴"

    def row(label, val):
        return f"<p><b>{label}:</b> {safe(val)}</p>"

    def srow(label, val):
        return f"<p><b>{label}:</b> {ic(val)} {safe(val)}</p>"

    return f"""
<p><b><u>Huntress</u></b></p>
{row("Device Name", a.get("hostname"))}
{row("Organization", a.get("organization_name"))}
{row("Serial Number", a.get("serial_number"))}
{row("Operating System", a.get("os"))}
{row("Platform", a.get("platform"))}
{row("Internal IP", a.get("ipv4_address"))}
{row("External IP", a.get("external_ip"))}
{row("Last Callback", a.get("last_callback_at"))}
{row("Last Survey", a.get("last_survey_at"))}
{row("Updated At", a.get("updated_at"))}
{row("Agent Version", a.get("version"))}
{row("EDR Version", a.get("edr_version"))}
{srow("Defender Status", a.get("defender_status"))}
{srow("Substatus", a.get("defender_substatus"))}
{srow("Policy", a.get("defender_policy_status"))}
{srow("Firewall", a.get("firewall_status"))}
""".strip()
