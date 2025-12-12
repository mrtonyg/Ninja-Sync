# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import re

def normalize(name):
    if not name:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", name).lower()


def strip_domain(name):
    """Return the hostname before the first dot."""
    if not name:
        return ""
    return name.split(".", 1)[0]


def match_by_name(ninja_devices, external_name):
    ext_norm = normalize(external_name)
    ext_base_norm = normalize(strip_domain(external_name))

    # 1. Exact full match
    for dev in ninja_devices:
        myname = dev.get("systemName") or dev.get("displayName") or ""
        my_norm = normalize(myname)
        if my_norm == ext_norm:
            return dev

    # 2. Match base host (clumsy == clumsy.promed.org)
    for dev in ninja_devices:
        myname = dev.get("systemName") or dev.get("displayName") or ""
        my_norm = normalize(myname)
        if my_norm == ext_base_norm:
            return dev

    # 3. Partial (prefix) match - cautious
    for dev in ninja_devices:
        myname = dev.get("systemName") or dev.get("displayName") or ""
        my_norm = normalize(myname)
        if ext_norm.startswith(my_norm):
            return dev

    # 4. Substring match as a fallback (optional)
    for dev in ninja_devices:
        myname = dev.get("systemName") or dev.get("displayName") or ""
        my_norm = normalize(myname)
        if my_norm in ext_norm:
            return dev

    return None

