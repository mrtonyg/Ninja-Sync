#!/usr/bin/env python3
"""
Huntress/Axcient to NinjaRMM Sync
Version: 1.0.0
Purpose: Main entry point for syncing Huntress and Axcient data to NinjaRMM custom fields
Usage: python3 sync2Ninja.py
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com
"""
import time

from mm_sync.config import LOG_PATH
from mm_sync.utils import log

from mm_sync.huntress import pull_huntress, enrich_huntress, html_huntress
from mm_sync.axcient import pull_axcient, html_axcient
from mm_sync.ninja_api import (
    ninja_get_all_devices,
    ninja_update_field
)
from mm_sync.matching import (
    build_device_maps,
    match_device
)


def main():
    log("[START] Sync2Ninja — Huntress + Axcient → Ninja")

    # ========================================================
    # 1. Huntress
    # ========================================================
    agents, orgs = pull_huntress()
    agents = enrich_huntress(agents, orgs)

    # ========================================================
    # 2. Ninja Device Inventory
    # ========================================================
    ninja_devices = ninja_get_all_devices()
    display_map, dns_map, system_map = build_device_maps(ninja_devices)

    # ========================================================
    # 3. Axcient x360Recover
    # ========================================================
    axcient_devices = pull_axcient()

    # ========================================================
    # 4. HUNTRESS → huntressStatus
    # ========================================================
    for agent in agents:
        name = agent.get("hostname")
        if not name:
            continue

        ninja_dev = match_device(name, display_map, dns_map, system_map)
        if not ninja_dev:
            continue

        nid = ninja_dev["id"]
        ninja_name = (
            ninja_dev.get("hostname") or
            ninja_dev.get("displayName") or
            ninja_dev.get("dnsName") or
            ninja_dev.get("systemName") or
            "Unknown"
        )

        html = html_huntress(agent)
        ninja_update_field(nid, "huntressStatus", html, name, ninja_name)
        time.sleep(0.1)

    # ========================================================
    # 5. AXCIENT → backupStatus
    # ========================================================
    for adev in axcient_devices:
        name = adev.get("name")
        if not name:
            continue

        ninja_dev = match_device(name, display_map, dns_map, system_map)
        if not ninja_dev:
            continue

        nid = ninja_dev["id"]
        ninja_name = (
            ninja_dev.get("hostname") or
            ninja_dev.get("displayName") or
            ninja_dev.get("dnsName") or
            ninja_dev.get("systemName") or
            "Unknown"
        )

        html = html_axcient(adev)
        ninja_update_field(nid, "backupStatus", html, name, ninja_name)
        time.sleep(0.1)

    log("[DONE] Sync Completed")


if __name__ == "__main__":
    main()
