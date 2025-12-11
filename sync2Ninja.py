"""
sync2Ninja.py
Version: 2.0.2
Author: Anthony George

Main synchronization engine:
    - Preflight validation (soft fail)
    - Fetch Huntress agents + org names
    - Fetch Axcient backup devices
    - Fetch NinjaOne devices
    - Match by displayName/dnsHostname/systemName
    - Update *two* separate Ninja fields:
        * huntressStatus
        * backupStatus
"""

from mm_sync.utils import log
from mm_sync.huntress import preflight_huntress, pull_huntress
from mm_sync.axcient import preflight_axcient, pull_axcient
from mm_sync.ninja_api import preflight_ninja, pull_ninja_devices, update_custom_field
from mm_sync.matching import find_device_match

# NEW: HTML builder module restored
from mm_sync.html_builder import (
    build_huntress_section,
    build_axcient_section,
)


# -------------------------------------------------------------------------
# PRE-FLIGHT CHECKS
# -------------------------------------------------------------------------
def preflight_all():
    log("Running preflight checks...")

    ok = True
    if not preflight_huntress():
        ok = False
    if not preflight_ninja():
        ok = False
    if not preflight_axcient():
        ok = False

    if not ok:
        log("One or more preflight checks failed (soft). Continuing...", "WARN")

    log("Preflight completed.")


# -------------------------------------------------------------------------
# MAIN SYNCHRONIZATION
# -------------------------------------------------------------------------
def main():
    log("[START] sync2Ninja 2.0.2")

    preflight_all()

    # Load Huntress and org names
    h_data = pull_huntress()
    agents = h_data["agents"]
    orgs = h_data["orgs"]

    # Load Axcient devices
    axcient_devices = pull_axcient()

    # Load Ninja devices
    ninja_devices = pull_ninja_devices()

    # ------------------------------------------------------------------
    # Process Huntress agents → huntressStatus field
    # ------------------------------------------------------------------
    for agent in agents:
        hostname = agent.get("hostname", "").lower()
        org_id = agent.get("organization_id")
        org_name = orgs.get(org_id, "Unknown")

        match = find_device_match(hostname, ninja_devices)
        if not match:
            continue

        device_id = match["id"]
        section = build_huntress_section(agent, org_name)

        payload = {"huntressStatus": section}
        if update_custom_field(device_id, payload):
            log(f"Updated huntressStatus for {hostname} → NinjaID {device_id}", "OK")

    # ------------------------------------------------------------------
    # Process Axcient backups → backupStatus field
    # ------------------------------------------------------------------
    for dev in axcient_devices:
        name = dev.get("name", "").lower()
        match = find_device_match(name, ninja_devices)
        if not match:
            continue

        device_id = match["id"]
        section = build_axcient_section(dev)

        payload = {"backupStatus": section}
        if update_custom_field(device_id, payload):
            log(f"Updated backupStatus for {name} → NinjaID {device_id}", "OK")

    log("[DONE] sync2Ninja Complete.")


# -------------------------------------------------------------------------
if __name__ == "__main__":
    main()
