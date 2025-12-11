#!/usr/bin/env python3
# ================================================================
#  sync2Ninja.py — Ninja-Sync v2.0.8
#  Media Managed — Anthony George
#  Root Orchestrator / CLI Entry Point
# ================================================================

import argparse
import sys
import time

from ninja_sync.core.logger import log, warn, error
from ninja_sync.core.config import DEBUG_MODE
from ninja_sync.core.cache import clear_cache_group
from ninja_sync.api.huntress_api import HuntressAPI
from ninja_sync.api.ninja_api import NinjaAPI
from ninja_sync.api.axcient_api import AxcientAPI
from ninja_sync.core.matching import DeviceMatcher
from ninja_sync.core.html_builder import (
    build_huntress_html,
    build_axcient_html
)


VERSION = "2.0.8"


# -------------------------------------------------------------------
# RUN FULL SYNC
# -------------------------------------------------------------------
def run_full_sync():
    log("[START] Full sync2Ninja workflow v" + VERSION)

    ninja = NinjaAPI()
    hunt = HuntressAPI()
    axc = AxcientAPI()
    matcher = DeviceMatcher()

    # --------------------------------------
    # PRE-FLIGHT CHECKS
    # --------------------------------------
    log("Running preflight checks...")

    ok_hunt = hunt.preflight()
    ok_ninja = ninja.preflight()
    ok_axc = axc.preflight()

    if not (ok_hunt and ok_ninja and ok_axc):
        warn("One or more preflight checks failed (soft). Continuing...")

    # --------------------------------------
    # FETCH + CACHE ALL PROVIDERS
    # --------------------------------------
    hunt_agents, hunt_orgs = hunt.get_cached_or_fetch()
    ninja_devices = ninja.get_cached_or_fetch()
    axcient_devices = axc.get_cached_or_fetch()

    # --------------------------------------
    # PROCESS HUNTRESS
    # --------------------------------------
    log("Processing Huntress...")
    for agent in hunt_agents:
        hostname = agent.get("hostname", "").strip()
        ninja_match = matcher.match_ninja_by_names(hostname, ninja_devices)
        if not ninja_match:
            warn(f"[HUNTRESS] Could not match device: {hostname}")
            continue

        html, text = build_huntress_html(agent, hunt_orgs)

        ninja.update_custom_field(
            device_id=ninja_match["id"],
            field_name="huntressStatus",
            html=html,
            text=text,
            src_name=hostname,
            ninja_name=ninja_match.get("displayName")
        )

    # --------------------------------------
    # PROCESS AXCIENT
    # --------------------------------------
    log("Processing Axcient...")
    for axdev in axcient_devices:
        name = axdev.get("name", "").strip()
        ninja_match = matcher.match_ninja_by_names(name, ninja_devices)
        if not ninja_match:
            warn(f"[AXCIENT] Could not match device: {name}")
            continue

        html, text = build_axcient_html(axdev)

        ninja.update_custom_field(
            device_id=ninja_match["id"],
            field_name="backupStatus",
            html=html,
            text=text,
            src_name=name,
            ninja_name=ninja_match.get("displayName")
        )

    log("[DONE] Sync Completed")
    return 0


# -------------------------------------------------------------------
# MAIN — CLI INTERFACE
# -------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Ninja-Sync v2.0.8 — Media Managed",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        help="Command to run: sync, preflight, clear-cache"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force refresh (ignore cache)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode at runtime"
    )

    parser.add_argument(
        "--cache-group",
        choices=["huntress", "ninja", "axcient", "all"],
        help="Which cache group to clear"
    )

    args = parser.parse_args()

    # Enable debug dynamically
    if args.debug:
        import ninja_sync.core.config as cfg
        cfg.DEBUG_MODE = True
        log("[DEBUG] Debug mode enabled via CLI flag")

    # --------------------------------------
    # NO COMMAND PROVIDED → run full sync
    # --------------------------------------
    if not args.command:
        warn("No command provided. Running full sync...")
        return run_full_sync()

    # --------------------------------------
    # COMMAND DISPATCH
    # --------------------------------------
    cmd = args.command.lower()

    if cmd == "sync":
        return run_full_sync()

    elif cmd == "preflight":
        log("Running explicit preflight checks...")
        ok1 = HuntressAPI().preflight()
        ok2 = NinjaAPI().preflight()
        ok3 = AxcientAPI().preflight()
        log("Preflight completed.")
        return 0

    elif cmd == "clear-cache":
        if not args.cache_group:
            error("Must specify --cache-group")
            return 1
        clear_cache_group(args.cache_group)
        return 0

    else:
        error(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
