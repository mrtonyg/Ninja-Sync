"""
Device Matching Logic
Version: 1.0.0
Purpose: Match Huntress/Axcient devices to NinjaRMM devices by hostname, DNS name, or system name
Usage: Called by sync2Ninja.py to correlate devices across platforms
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com
"""
from .utils import norm, log


def build_device_maps(devs):
    display_map = {}
    dns_map = {}
    system_map = {}

    for d in devs:
        if d.get("displayName"):
            display_map[norm(d["displayName"])] = d
        if d.get("dnsName"):
            dns_map[norm(d["dnsName"])] = d
        if d.get("systemName"):
            system_map[norm(d["systemName"])] = d

    return display_map, dns_map, system_map


def match_device(name, display_map, dns_map, system_map):
    key = norm(name)

    if key in display_map:
        return display_map[key]
    if key in dns_map:
        return dns_map[key]
    if key in system_map:
        return system_map[key]

    log(f"[WARN] No Ninja match: {name}")
    return None
