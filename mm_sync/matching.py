"""
Device Matching Logic
Author: Anthony George
Version: 2.0.5
"""

from utils import warn

def match_huntress_to_ninja(agent, ninja_devices):
    sn = (agent.get("serial_number") or "").lower()
    hn = (agent.get("hostname") or "").lower()

    for d in ninja_devices:
        names = [
            (d.get("displayName") or "").lower(),
            (d.get("dnsName") or "").lower(),
            (d.get("systemName") or "").lower()
        ]
        if sn and sn in str(d).lower():
            return d
        if hn in names:
            return d

    warn(f"Huntress: no match for {hn}")
    return None

def match_axcient_to_ninja(device, ninja_devices):
    name = (device.get("name") or "").split(".")[0].lower()

    for d in ninja_devices:
        names = [
            (d.get("displayName") or "").split(".")[0].lower(),
            (d.get("dnsName") or "").split(".")[0].lower(),
            (d.get("systemName") or "").split(".")[0].lower()
        ]
        if name in names:
            return d

    warn(f"Axcient: no match for {device.get('name')}")
    return None
