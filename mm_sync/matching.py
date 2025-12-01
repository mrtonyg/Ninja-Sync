# matching.py
# Device name matching logic for Huntress/Axcient → NinjaOne

from .utils import log

# ------------------------------------------------------------
# Normalization helpers
# ------------------------------------------------------------
def norm(s):
    if not s:
        return ""
    return s.strip().lower()

def base_hostname(name):
    # Strip domain suffix if present
    if not name:
        return ""
    return name.split(".")[0].lower()

# ------------------------------------------------------------
# Build lookup maps for Ninja devices
# ------------------------------------------------------------
def build_device_maps(devices):
    display_map = {}
    dns_map = {}
    system_map = {}
    base_map = {}

    for d in devices:
        did = d.get("id")

        dn = norm(d.get("displayName"))
        if dn:
            display_map[dn] = d

        dns = norm(d.get("dnsName"))
        if dns:
            dns_map[dns] = d
            base_map[base_hostname(dns)] = d

        sysn = norm(d.get("systemName"))
        if sysn:
            system_map[sysn] = d

    return display_map, dns_map, system_map, base_map

# ------------------------------------------------------------
# Match a device name to Ninja device list
# ------------------------------------------------------------
def match_device(name, display_map, dns_map, system_map, base_map):
    if not name:
        return None

    n = norm(name)
    b = base_hostname(n)

    # 1) Exact displayName
    if n in display_map:
        return display_map[n]

    # 2) Exact dnsName
    if n in dns_map:
        return dns_map[n]

    # 3) Exact systemName
    if n in system_map:
        return system_map[n]

    # 4) Stripped base hostname (FQDN → hostname)
    if b in base_map:
        return base_map[b]

    log(f"[WARN] Could not match device: {name}")
    return None
