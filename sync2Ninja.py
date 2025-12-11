"""
sync2Ninja Main Program
Author: Anthony George
Version: 2.0.6
"""

from mm_sync.utils import log, warn, error
from mm_sync.huntress import pull_huntress, preflight_huntress
from mm_sync.axcient import pull_axcient, preflight_axcient
from mm_sync.ninja_api import pull_ninja_devices, ninja_update_field, preflight_ninja
from mm_sync.matching import match_huntress_to_ninja, match_axcient_to_ninja
from mm_sync.html_builder import build_huntress_html, build_axcient_html
from mm_sync.config import (
    NINJA_FIELD_HUNTRESS,
    NINJA_FIELD_AXCIENT
)

def run_preflight():
    log("Running preflight checks...")

    ok_h = preflight_huntress()
    if not ok_h:
        warn("Huntress preflight failed (soft)")

    ok_n = preflight_ninja()
    if not ok_n:
        warn("NinjaOne preflight failed (soft)")

    ok_a = preflight_axcient()
    if not ok_a:
        warn("Axcient preflight failed (soft)")

    if ok_h and ok_n and ok_a:
        log("All preflight checks OK")
    else:
        warn("One or more preflight checks failed (soft). Continuing...")

def main():
    log("[START] sync2Ninja 2.0.6")

    run_preflight()

    # Load full datasets
    agents, orgs = pull_huntress()
    ninja_devices = pull_ninja_devices()
    axcient_devices = pull_axcient()

    # -----------------------------------------------------------------
    # PROCESS HUNTRESS → NINJA
    # -----------------------------------------------------------------
    log("Processing Huntress...")
    for agent in agents:
        org_name = orgs.get(agent.get("organization_id"), "Unknown")

        ninja = match_huntress_to_ninja(agent, ninja_devices)
        if not ninja:
            continue

        device_id = ninja["id"]
        html, text = build_huntress_html(agent, org_name)
        ninja_update_field(device_id, NINJA_FIELD_HUNTRESS, html, text)

    # -----------------------------------------------------------------
    # PROCESS AXCIENT → NINJA
    # -----------------------------------------------------------------
    log("Processing Axcient...")
    for axdev in axcient_devices:
        ninja = match_axcient_to_ninja(axdev, ninja_devices)
        if not ninja:
            continue

        device_id = ninja["id"]
        html, text = build_axcient_html(axdev)
        ninja_update_field(device_id, NINJA_FIELD_AXCIENT, html, text)

    log("[DONE] Sync complete")

if __name__ == "__main__":
    main()
