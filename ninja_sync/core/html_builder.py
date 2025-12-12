# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

from datetime import datetime

def row(label, value):
    return f"<b>{label}:</b> {value}<br>"

def build_huntress_html(agent, org_map):
    if not agent:
        return "<b>No Huntress data.</b>", "No Huntress data."
    hostname = agent.get("hostname") or "Unknown"
    os_name = agent.get("os") or "Unknown"
    os_build = agent.get("os_build_version")
    org_name = org_map.get(str(agent.get("organization_id")), "Unknown")
    os_full = f"{os_name} (Build {os_build})" if os_build else os_name
    defender_status = agent.get("defender_status") or "Unknown"
    defender_policy = agent.get("defender_policy_status") or "Unknown"
    defender_substatus = agent.get("defender_substatus") or "Unknown"

    firewall = agent.get("firewall_status") or "Unknown"

    agent_version = agent.get("version") or "Unknown"
    edr_version = agent.get("edr_version") or "Unknown"

    last_callback = agent.get("last_callback_at") or "Unknown"

    html = (
        "<b>Huntress Status</b><br>"
        f"{row('Device Name', agent.get('hostname'))}"
        f"{row('Organization', org_name)}"
        f"{row('OS', os_full)}"
        f"{row('Defender',f'{defender_status}, {defender_policy}, {defender_substatus}')}"
        f"{row('Agent Version', f'{agent_version}, EDR {edr_version}')}"
        f"{row('Last Callback', last_callback)}"
    )

    return html, html.replace("<br>", "\n")

def build_axcient_html(device):
    if not device:
        return "<b>No backup data.</b>", "No backup data."

    av = device.get("latest_autoverify_details") or {}
    av_status = "Unknown"
    if av:
        healthy = av.get("is_healthy")
        av_status = f"{'🟢' if healthy else '🔴'} {av.get('status', 'n/a')} ({av.get('timestamp', '')})"

    health = device.get("current_health_status") or {}
    health_status = f"{health.get('status', 'Unknown')} ({health.get('timestamp','')})"

    html = (
        "<b>Axcient Backup Status</b><br>"
        f"{row('Name', device.get('name'))}"
        f"{row('Agent Version', device.get('agent_version'))}"
        f"{row('Current Status', health_status)}"
        f"{row('Latest Cloud RP', device.get('latest_cloud_rp','N/A'))}"
        f"{row('AutoVerify Result', av_status)}"
    )

    return html, html.replace("<br>", "\n")
