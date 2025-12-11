# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import os
from ninja_sync.api.huntress_api import HuntressAPI
from ninja_sync.api.axcient_api import AxcientAPI
from ninja_sync.api.ninja_api import NinjaAPI
from ninja_sync.core.logger import info, warn, error
from ninja_sync.core.cache import load_cache, write_cache
from ninja_sync.core import config
from ninja_sync.core.html_builder import build_huntress_html, build_axcient_html
from ninja_sync.core.matching import match_by_name

def preflight(huntress, ninja, axcient):
    info("Running preflight checks...")

    # Huntress
    agents = huntress.get_agents()
    if not agents:
        warn("Huntress preflight failed (soft)")
    else:
        info("Huntress preflight OK")

    # Ninja
    if not ninja.authenticate():
        warn("Ninja preflight failed (soft)")
    else:
        info("Ninja preflight OK")

    # Axcient
    devices = axcient.get_devices()
    if not devices:
        warn("Axcient preflight failed (soft)")
    else:
        info("Axcient preflight OK")

    warn("One or more preflight checks may have failed. Continuing...")

def main():
    info("[START] sync2Ninja 2.0.9")

    huntress = HuntressAPI()
    ninja = NinjaAPI()
    axcient = AxcientAPI()

    preflight(huntress, ninja, axcient)

    # Huntress
    h_agents = huntress.get_agents()
    h_orgs = huntress.get_orgs()
    org_map = {str(o["id"]): o.get("name","Unknown") for o in h_orgs}

    write_cache(config.HUNTRESS_CACHE_AGENTS, h_agents)
    write_cache(config.HUNTRESS_CACHE_ORGS, h_orgs)

    # Axcient
    ax_list = axcient.get_devices()
    write_cache(config.AXCIENT_CACHE, ax_list)

    # Ninja devices
    if not ninja.authenticate():
        error("Cannot authenticate Ninja. Exiting.")
        return

    ninja_devices = ninja.get_devices()
    write_cache(config.NINJA_CACHE_DEVICES, ninja_devices)

    # PROCESS HUNTRESS
    for agent in h_agents:
        match = match_by_name(ninja_devices, agent.get("hostname"))
        if not match:
            warn(f"No Ninja match for Huntress device {agent.get('hostname')}")
            continue

        html, _ = build_huntress_html(agent, org_map)
        ninja.update_custom_field(match["id"], config.CUSTOM_FIELD_HUNTRESS, html)

    # PROCESS AXCIENT
    for dev in ax_list:
        match = match_by_name(ninja_devices, dev.get("name"))
        if not match:
            warn(f"No Ninja match for Axcient device {dev.get('name')}")
            continue

        html, _ = build_axcient_html(dev)
        ninja.update_custom_field(match["id"], config.CUSTOM_FIELD_AXCIENT, html)

    info("[DONE] Sync completed.")

if __name__ == "__main__":
    main()
