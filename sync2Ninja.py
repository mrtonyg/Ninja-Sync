#!/usr/bin/env python3
# sync2Ninja.py
# Main orchestrator for Huntress + Axcient → NinjaOne

import sys
import time

from mm_sync.utils import (
    log, clear_huntress_cache, clear_axcient_cache,
    clear_ninja_cache, clear_all_caches
)
from mm_sync.huntress import pull_huntress, enrich_huntress, html_huntress
from mm_sync.axcient import pull_axcient, html_axcient
from mm_sync.ninja_api import ninja_get_all_devices, ninja_update_field
from mm_sync.matching import build_device_maps, match_device

# ------------------------------------------------------------
# CLI options
# ------------------------------------------------------------
def handle_cli_flags():
    flags = sys.argv[1:]
    if not flags:
        return False

    if "--clear-huntress" in flags:
        clear_huntress_cache()
        return True
    if "--clear-axcient" in flags:
        clear_axcient_cache()
        return True
    if "--clear-ninja" in flags:
        clear_ninja_cache()
        return True
    if "--clear-all" in flags:
        clear_all_caches()
        return True
    if "--clear-cache" in flags:
        print("Select cache to clear:")
        print("1. Huntress")
        print("2. Axcient")
        print("3. NinjaOne")
        print("4. All")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            clear_huntress_cache()
        elif choice == "2":
            clear_axcient_cache()
        elif choice == "3":
            clear_ninja_cache()
        elif choice == "4":
            clear_all_caches()
        return True

    return False

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    log("[START] sync2Ninja")

    if handle_cli_flags():
        return

    # --------------------------------------------------------
    # Huntress
    # --------------------------------------------------------
    agents, orgs = pull_huntress()
    agents = enrich_huntress(agents, orgs)

    # --------------------------------------------------------
    # Ninja Inventory
    # --------------------------------------------------------
    ninja_devices = ninja_get_all_devices()
    display_map, dns_map, system_map, base_map = build_device_maps(ninja_devices)

    # --------------------------------------------------------
    # Axcient
    # --------------------------------------------------------
    axcient_devices = pull_axcient()

    # --------------------------------------------------------
    # Process Huntress → Ninja
    # --------------------------------------------------------
    for agent in agents:
        hn = agent.get("hostname")
        if not hn:
            continue

        ninja_dev = match_device(hn, display_map, dns_map, system_map, base_map)
        if not ninja_dev:
            continue

        nid = ninja_dev.get("id")
        ninja_name = ninja_dev.get("displayName") or ninja_dev.get("dnsName") or ninja_dev.get("systemName")

        html = html_huntress(agent)
        ninja_update_field(nid, "huntressStatus", html, hn, ninja_name)
        time.sleep(0.2)

    # --------------------------------------------------------
    # Process Axcient → Ninja
    # --------------------------------------------------------
    for ax in axcient_devices:
        name = ax.get("name")
        if not name:
            continue

        ninja_dev = match_device(name, display_map, dns_map, system_map, base_map)
        if not ninja_dev:
            continue

        nid = ninja_dev.get("id")
        ninja_name = ninja_dev.get("displayName") or ninja_dev.get("dnsName") or ninja_dev.get("systemName")

        html = html_axcient(ax)
        ninja_update_field(nid, "backupStatus", html, name, ninja_name)
        time.sleep(0.2)

    log("[DONE] Sync Completed")


if __name__ == "__main__":
    main()

