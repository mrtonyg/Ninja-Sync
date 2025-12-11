# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

from datetime import datetime

def row(label, value):
    return f"<b>{label}:</b> {value}<br>"

def build_huntress_html(agent, org_map):
    if not agent:
        return "<b>No Huntress data.</b>", "No Huntress data."

    org_name = org_map.get(str(agent.get("organization_id")), "Unknown")

    html = (
        "<b>Huntress Status</b><br>"
        f"{row('Device Name', agent.get('hostname'))}"
        f"{row('Organization', org_name)}"
        f"{row('OS', agent.get('os_info', {}).get('os', 'Unknown'))}"
        f"{row('Agent Version', agent.get('agent_version', 'N/A'))}"
        f"{row('Last Callback', agent.get('last_callback', 'N/A'))}"
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
