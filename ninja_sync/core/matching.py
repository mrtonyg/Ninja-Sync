# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import re

def normalize(name):
    if not name:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", name).lower()

def match_by_name(ninja_devices, external_name):
    ext_norm = normalize(external_name)
    for dev in ninja_devices:
        myname = dev.get("systemName") or dev.get("displayName") or ""
        if normalize(myname) == ext_norm:
            return dev
    return None
