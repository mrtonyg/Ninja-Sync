"""
sync2Ninja.py
Version: 2.0.1
Author: Anthony George
"""

import sys
from mm_sync.utils import log
from mm_sync.huntress import preflight_huntress, pull_huntress
from mm_sync.axcient import preflight_axcient, pull_axcient
from mm_sync.ninja_api import preflight_ninja, pull_ninja_devices, update_custom_field
from mm_sync.matching import find_device_match


# -------------------------------------------------------------------------
# Preflight Orchestration
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
# Build HTML fragment for Axcient device
# -------------------------------------------------------------------------
def make_backup_html(dev):
    status = dev["current_health_status"]["status"]
    ts = dev["current_health_status"]["timestamp"]

    av = dev.get("latest_autoverify_details")
    av_status = av.get("status") if av else "unknown"
    av_ts = av.get("timestamp") if av else "unknown"

    cloud_rp = dev.get("latest_cloud_rp", "unknown")

    html = f"""
Backup Status
-------------
Name: {dev['name']}
Current Status: {status} ({ts})

AutoVerify: {av_status} ({av_ts})
Latest Cloud RP: {cloud_rp}
"""
    return html.strip()


# -------------------------------------------------------------------------
# MAIN SYNC
# -------------------------------------------------------------------------
def main():
    log("[START] sync2Ninja")

    preflight_all()

    huntress = pull_huntress()
    axcient = pull_axcient()
    ninja = pull_ninja_devices()

    for dev in axcient:
        ninja_match = find_device_match(dev["name"], ninja)
        if not ninja_match:
            continue

        device_id = ninja_match["id"]
        html = make_backup_html(dev)

        payload = {"backupStatus": html}
        if update_custom_field(device_id, payload):
            log(f"Updated backupStatus for {dev['name']} → NinjaID {device_id}", "OK")

    log("[DONE] Sync complete.")


if __name__ == "__main__":
    main()
