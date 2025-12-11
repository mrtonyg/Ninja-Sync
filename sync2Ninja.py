"""
sync2Ninja Main Program
Author: Anthony George
Version: 2.0.5
"""

from utils import log, warn, error
from huntress import pull_huntress, preflight_huntress
from axcient import pull_axcient, preflight_axcient
from ninja_api import pull_ninja_devices, ninja_update_field, preflight_ninja
from matching import match_huntress_to_ninja, match_axcient_to_ninja
from html_builder import build_huntress_html, build_axcient_html
from config import NINJA_FIELD_HUNTRESS, NINJA_FIELD_AXCIENT

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
    log("[START] sync2Ninja 2.0.5")

    run_preflight()

    agents, orgs = pull_huntress()
    ninja = pull_ninja_devices()
    axcient = pull_axcient()

    log("Processing Huntress...")
    for agent in agents:
        org_name = orgs.get(agent.get("organization_id"), "Unknown")
        ninja_dev = match_huntress_to_ninja(agent, ninja)
        if not ninja_dev:
            continue

        device_id = ninja_dev["id"]
        html, text = build_huntress_html(agent, org_name)
        ninja_update_field(device_id, NINJA_FIELD_HUNTRESS, html, text)

    log("Processing Axcient...")
    for device in axcient:
        ninja_dev = match_axcient_to_ninja(device, ninja)
        if not ninja_dev:
            continue

        device_id = ninja_dev["id"]
        html, text = build_axcient_html(device)
        ninja_update_field(device_id, NINJA_FIELD_AXCIENT, html, text)

    log("[DONE] Sync complete")

if __name__ == "__main__":
    main()
