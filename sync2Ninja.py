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
# Preflight Checks
# ------------------------------------------------------------
from mm_sync.huntress import huntress_raw_get
from mm_sync.ninja_api import (
    ninja_get_token,
    ninja_get_all_devices
)
from mm_sync.axcient import axcient_raw_get


def preflight_checks():
    log("[INFO] Running preflight checks...")

    # ------------------------------------
    # 1. Check Huntress Authentication
    # ------------------------------------
    try:
        resp = huntress_raw_get("/agents", params={"page": 1})
        if resp is None:
            log_error("[FAIL] Huntress authentication failed.")
            return False
    except Exception as e:
        log_error("[FAIL] Huntress API unreachable or invalid credentials.", exc=e)
        return False
    log("[OK] Huntress authentication verified.")

    # ------------------------------------
    # 2. Check NinjaOne OAuth & Scopes
    # ------------------------------------
    token = ninja_get_token()
    if not token:
        log_error("[FAIL] NinjaOne OAuth token could not be obtained.")
        return False

    # Validate token by performing a harmless request
    devices = ninja_get_all_devices(force_refresh=True)
    if devices is None or devices == []:
        log_error(
            "[FAIL] NinjaOne API credentials valid, but device list came back empty. "
            "This usually indicates missing OAuth scopes: "
            "device:read, device:write, customfield:read, customfield:write"
        )
        return False

    log(f"[OK] NinjaOne OAuth verified. {len(devices)} devices accessible.")

    # ------------------------------------
    # 3. Check Axcient API Key
    # ------------------------------------
    try:
        test = axcient_raw_get("/device", {"limit": 1, "offset": 0})
        if not test:
            log_error("[FAIL] Axcient API key invalid or no access.")
            return False
    except Exception as e:
        log_error("[FAIL] Axcient API unreachable or invalid key.", exc=e)
        return False

    log("[OK] Axcient API key verified.")

    # ------------------------------------
    # All checks passed
    # ------------------------------------
    log("[INFO] All preflight checks passed successfully.\n")
    return True

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    log("[START] sync2Ninja")

    if handle_cli_flags():
        return

    # ----------------------------------------
    # Preflight check BEFORE doing any work
    # ----------------------------------------
    if not preflight_checks():
        log("[ABORT] Preflight checks failed. Sync halted.\n")
        return

    # ----------------------------------------
    # Pull Huntress
    # ----------------------------------------
    agents, orgs = pull_huntress()
    agents = enrich_huntress(agents, orgs)

    # ----------------------------------------
    # Ninja Devices
    # ----------------------------------------
    ninja_devices = ninja_get_all_devices()
    display_map, dns_map, system_map, base_map = build_device_maps(ninja_devices)

    # ----------------------------------------
    # Axcient Devices
    # ----------------------------------------
    axcient_devices = pull_axcient()

    # ----------------------------------------
    # Sync Huntress → Ninja
    # ----------------------------------------
    for agent in agents:
        hn = agent.get("hostname")
        if not hn:
            continue

        ninja_dev = match_device(hn, display_map, dns_map, system_map, base_map)
        if not ninja_dev:
            continue

        nid = ninja_dev.get("id")
        ninja_name = (
            ninja_dev.get("displayName")
            or ninja_dev.get("dnsName")
            or ninja_dev.get("systemName")
        )

        html = html_huntress(agent)
        ninja_update_field(nid, "huntressStatus", html, hn, ninja_name)
        time.sleep(0.2)

    # ----------------------------------------
    # Sync Axcient → Ninja
    # ----------------------------------------
    for ax in axcient_devices:
        name = ax.get("name")
        if not name:
            continue

        ninja_dev = match_device(name, display_map, dns_map, system_map, base_map)
        if not ninja_dev:
            continue

        nid = ninja_dev.get("id")
        ninja_name = (
            ninja_dev.get("displayName")
            or ninja_dev.get("dnsName")
            or ninja_dev.get("systemName")
        )

        html = html_axcient(ax)
        ninja_update_field(nid, "backupStatus", html, name, ninja_name)
        time.sleep(0.2)

    log("[DONE] Sync Completed")


if __name__ == "__main__":
    main()

