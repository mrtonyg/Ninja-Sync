"""
sync2Ninja.py
Version: 2.0.3
Author: Anthony George

Syncs Huntress + Axcient → NinjaOne custom fields.
"""

from mm_sync.utils import log
from mm_sync.huntress import preflight_huntress, pull_huntress
from mm_sync.axcient import preflight_axcient, pull_axcient
from mm_sync.ninja_api import preflight_ninja, pull_ninja_devices, update_custom_field
from mm_sync.matching import find_device_match
from mm_sync.html_builder import build_huntress_section, build_axcient_section


# -------------------------------------------------------------------------
# PRE-FLIGHT
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
# MAIN
# -------------------------------------------------------------------------
def main():
    log("[START] sync2Ninja 2.0.3")

    preflight_all()

    # Huntress
    h_data = pull_huntress()
    agents = h_data["agents"]
    orgs = h_data["orgs"]

    # Axcient
    axcient_data = pull_axcient()

    # Ninja
    ninja_devices = pull_ninja_devices()

    # --------------------------------------------------------------
    # HUNTRESS SYNC
    # --------------------------------------------------------------
    for agent in agents:
        hostname = agent.get("hostname", "").lower()
        org_name = orgs.get(agent.get("organization_id"), "Unknown")

        match = find_device_match(hostname, ninja_devices)
        if not match:
            continue

        ninja_id = match["id"]
        html = build_huntress_section(agent, org_name)

        if update_custom_field(ninja_id, {"huntressStatus": html}):
            log(f"Updated huntressStatus for {hostname} → {ninja_id}", "OK")

    # --------------------------------------------------------------
    # AXCIENT SYNC
    # --------------------------------------------------------------
    for dev in axcient_data:
        name = dev.get("name", "").lower()
        match = find_device_match(name, ninja_devices)

        if not match:
            continue

        ninja_id = match["id"]
        html = build_axcient_section(dev)

        if update_custom_field(ninja_id, {"backupStatus": html}):
            log(f"Updated backupStatus for {name} → {ninja_id}", "OK")

    log("[DONE] sync2Ninja complete.")


if __name__ == "__main__":
    main()
