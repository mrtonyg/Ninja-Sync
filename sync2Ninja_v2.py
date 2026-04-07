#!/usr/bin/env python3
"""
Huntress/Axcient to NinjaRMM Sync (Streamlined)
Version: 2.0.0
Purpose: Main entry point for syncing Huntress and Axcient data to NinjaRMM custom fields
Usage: python3 sync2Ninja_v2.py [--force-refresh] [--parallel]
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com

Improvements in v2.0.0:
- Eliminated code duplication with generic sync_devices function
- Added parallel processing option for faster updates
- Better error handling with per-device try/catch
- Summary statistics at completion
- Command-line arguments support
"""
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def get_ninja_device_name(ninja_dev):
    """Extract the best available name from a Ninja device."""
    return (
        ninja_dev.get("hostname") or
        ninja_dev.get("displayName") or
        ninja_dev.get("dnsName") or
        ninja_dev.get("systemName") or
        "Unknown"
    )


def sync_single_device(device, field_name, html_generator, device_maps, rate_limit=0.1):
    """
    Sync a single device to NinjaRMM.
    
    Args:
        device: Source device dict (Huntress agent or Axcient device)
        field_name: NinjaRMM custom field name ('huntressStatus' or 'backupStatus')
        html_generator: Function to generate HTML from device data
        device_maps: Tuple of (display_map, dns_map, system_map)
        rate_limit: Sleep time between updates (seconds)
    
    Returns:
        Tuple of (success: bool, device_name: str, error_msg: str or None)
    """
    try:
        # Extract device name
        name = device.get("hostname") or device.get("name")
        if not name:
            return (False, "Unknown", "No hostname/name field")
        
        # Match to Ninja device
        display_map, dns_map, system_map = device_maps
        ninja_dev = match_device(name, display_map, dns_map, system_map)
        if not ninja_dev:
            return (False, name, "No Ninja match found")
        
        # Get Ninja device details
        nid = ninja_dev["id"]
        ninja_name = get_ninja_device_name(ninja_dev)
        
        # Generate HTML and update
        html = html_generator(device)
        ninja_update_field(nid, field_name, html, name, ninja_name)
        
        # Rate limiting
        if rate_limit > 0:
            time.sleep(rate_limit)
        
        return (True, name, None)
        
    except Exception as e:
        device_name = device.get("hostname") or device.get("name") or "Unknown"
        return (False, device_name, str(e))


def sync_devices_sequential(devices, field_name, html_generator, device_maps, rate_limit=0.1):
    """Sync devices sequentially (original behavior)."""
    results = []
    for device in devices:
        result = sync_single_device(device, field_name, html_generator, device_maps, rate_limit)
        results.append(result)
    return results


def sync_devices_parallel(devices, field_name, html_generator, device_maps, max_workers=5):
    """Sync devices in parallel using ThreadPoolExecutor."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(sync_single_device, device, field_name, html_generator, device_maps, 0): device
            for device in devices
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    return results


def print_summary(source_name, results):
    """Print summary statistics for a sync operation."""
    total = len(results)
    successful = sum(1 for r in results if r[0])
    failed = total - successful
    
    log(f"[SUMMARY] {source_name}: {successful}/{total} successful, {failed} failed")
    
    # Log failures
    if failed > 0:
        log(f"[FAILURES] {source_name} sync failures:")
        for success, name, error in results:
            if not success:
                log(f"  - {name}: {error}")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Sync Huntress/Axcient to NinjaRMM")
    parser.add_argument("--parallel", action="store_true", help="Use parallel processing for faster syncs")
    parser.add_argument("--max-workers", type=int, default=5, help="Max parallel workers (default: 5)")
    args = parser.parse_args()
    
    log("[START] Sync2Ninja v2.0 — Huntress + Axcient → Ninja")
    log(f"[CONFIG] Mode: {'Parallel' if args.parallel else 'Sequential'}")
    
    # ========================================================
    # 1. Pull data from all sources
    # ========================================================
    log("[FETCH] Pulling Huntress agents...")
    agents, orgs = pull_huntress()
    agents = enrich_huntress(agents, orgs)
    log(f"[FETCH] Retrieved {len(agents)} Huntress agents")
    
    log("[FETCH] Pulling Ninja devices...")
    ninja_devices = ninja_get_all_devices()
    device_maps = build_device_maps(ninja_devices)
    log(f"[FETCH] Retrieved {len(ninja_devices)} Ninja devices")
    
    log("[FETCH] Pulling Axcient devices...")
    axcient_devices = pull_axcient()
    log(f"[FETCH] Retrieved {len(axcient_devices)} Axcient devices")
    
    # ========================================================
    # 2. Sync Huntress → huntressStatus
    # ========================================================
    log("[SYNC] Syncing Huntress agents...")
    if args.parallel:
        huntress_results = sync_devices_parallel(
            agents, "huntressStatus", html_huntress, device_maps, args.max_workers
        )
    else:
        huntress_results = sync_devices_sequential(
            agents, "huntressStatus", html_huntress, device_maps, rate_limit=0.1
        )
    print_summary("Huntress", huntress_results)
    
    # ========================================================
    # 3. Sync Axcient → backupStatus
    # ========================================================
    log("[SYNC] Syncing Axcient devices...")
    if args.parallel:
        axcient_results = sync_devices_parallel(
            axcient_devices, "backupStatus", html_axcient, device_maps, args.max_workers
        )
    else:
        axcient_results = sync_devices_sequential(
            axcient_devices, "backupStatus", html_axcient, device_maps, rate_limit=0.1
        )
    print_summary("Axcient", axcient_results)
    
    # ========================================================
    # 4. Overall Summary
    # ========================================================
    total_devices = len(huntress_results) + len(axcient_results)
    total_success = sum(1 for r in huntress_results + axcient_results if r[0])
    
    log(f"[DONE] Sync Completed: {total_success}/{total_devices} devices updated successfully")


if __name__ == "__main__":
    main()
