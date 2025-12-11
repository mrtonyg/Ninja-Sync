"""
HTML Builder for NinjaOne WYSIWYG
Author: Anthony George
Version: 2.0.6
"""

from mm_sync.utils import strip_html

# ------------------------------------------------------
# Last-known-good Format D  (your proven stable layout)
# ------------------------------------------------------
def build_huntress_html(agent, org_name):

    def row(label, value):
        return f"<b>{label}:</b> {value}<br>\n"

    html = f"""
<h3>Huntress Status</h3>

<b>Information</b><br>
{row("Device Name", agent.get("hostname"))}
{row("Organization", org_name)}
{row("Serial Number", agent.get("serial_number"))}
{row("Operating System", agent.get("os"))}
{row("Platform", agent.get("platform"))}
{row("Internal IP", agent.get("ipv4_address"))}
{row("External IP", agent.get("external_ip"))}

<b>Times</b><br>
{row("Last Callback", agent.get("last_callback_at"))}
{row("Last Survey", agent.get("last_survey_at"))}
{row("Updated At", agent.get("updated_at"))}

<b>Versions</b><br>
{row("Agent Version", agent.get("version"))}
{row("EDR Version", agent.get("edr_version"))}

<b>Status</b><br>
{row("Defender Status", f"🟢 {agent.get('defender_status')}")}
{row("Defender Substatus", f"🟢 {agent.get('defender_substatus')}")}
{row("Defender Policy", f"🟢 {agent.get('defender_policy_status')}")}
{row("Firewall Status", f"🟢 {agent.get('firewall_status')}")}
"""

    return html.strip(), strip_html(html)


def build_axcient_html(device):

    def row(label, value):
        return f"<b>{label}:</b> {value}<br>\n"

    health = device.get("current_health_status", {})
    av = device.get("latest_autoverify_details", {})

    html = f"""
<h3>Axcient Backup Status</h3>

<b>Information</b><br>
{row("Device Name", device.get("name"))}
{row("IP Address", device.get("ip_address"))}
{row("Operating System", device.get("os", {}).get("os_name"))}

<b>Current Status</b><br>
{row("Status", f"🟢 {health.get('status')} ({health.get('timestamp')})")}

<b>AutoVerify</b><br>
{row("Result", f"{'🟢' if av.get('is_healthy') else '🔴'} {av.get('status')} ({av.get('timestamp')})")}

<b>Recovery Points</b><br>
{row("Latest Cloud RP", device.get("latest_cloud_rp"))}

<b>Agent</b><br>
{row("Agent Version", device.get("agent_version"))}
"""

    return html.strip(), strip_html(html)
