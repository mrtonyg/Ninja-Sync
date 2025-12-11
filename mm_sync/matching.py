"""
matching.py
Version: 2.0.1
Author: Anthony George
"""

from mm_sync.utils import log


# -------------------------------------------------------------------------
# Serial, DNS, Display name matching (fallback chain)
# -------------------------------------------------------------------------
def find_device_match(ax_name, ninja_devices):
    ax_lower = ax_name.lower()

    # 1. Exact match on displayName
    for d in ninja_devices:
        if d.get("displayName", "").lower() == ax_lower:
            return d

    # 2. Match dnsHostname
    for d in ninja_devices:
        if d.get("dnsHostname", "").lower() == ax_lower:
            return d

    # 3. System name
    for d in ninja_devices:
        if d.get("systemName", "").lower() == ax_lower:
            return d

    log(f"Could not match device: {ax_name}", "WARN")
    return None
