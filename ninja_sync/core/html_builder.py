"""
HTML Builder for NinjaOne WYSIWYG
Author: Anthony George
Version: 2.0.6
"""

from ..utils import strip_html

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
    """
    Build condensed 2-column HTML for Axcient status.
    Safe against missing autoverify_details, missing jobs, missing timestamps.
    """
    name = device.get("name", "Unknown")
    agent_version = device.get("agent_version", "Unknown")

    current = device.get("current_health_status") or {}
    curr_status = current.get("status", "Unknown")
    curr_ts = current.get("timestamp", "Unknown")

    # Autoverify may be NULL
    av = device.get("latest_autoverify_details") or {}
    av_status = av.get("status", "none")
    av_ts = av.get("timestamp", "Unknown")
    av_result_icon = "🟢" if av.get("is_healthy") else "🔴"

    latest_cloud_rp = device.get("latest_cloud_rp", "Unknown")

    # Jobs are optional
    jobs = device.get("jobs") or []
    cloud_job = jobs[0] if jobs else {}
    job_latest_rp = cloud_job.get("latest_rp", "Unknown")
    job_health = cloud_job.get("health_status", "Unknown")
    job_icon = "🟢" if job_health == "NORMAL" else "🔴"

    def row(label, value):
        return (
            f"<div style='display:flex;'>"
            f"<div style='width:140px;font-weight:bold;'>{label}:</div>"
            f"<div>{value}</div>"
            f"</div>"
        )

    html = f"""
<h3 style="margin-bottom:6px;">Axcient Backup Status</h3>
{row("Device", name)}
{row("Agent Ver", agent_version)}
{row("Current Status", f"{'🟢' if curr_status == 'NORMAL' else '🔴'} {curr_status} ({curr_ts})")}
{row("Cloud RP", latest_cloud_rp)}
{row("Job RP", f"{job_icon} {job_latest_rp}")}
{row("AutoVerify", f"{av_result_icon} {av_status} ({av_ts})")}
"""

    # Plain-text version for Ninja One WYSIWYG "text" field
    text = (
        f"Axcient Backup Status\n"
        f"- Device: {name}\n"
        f"- Agent Ver: {agent_version}\n"
        f"- Current Status: {curr_status} ({curr_ts})\n"
        f"- Cloud RP: {latest_cloud_rp}\n"
        f"- Job RP: {job_latest_rp} ({job_health})\n"
        f"- AutoVerify: {av_status} ({av_ts})\n"
    )

    return html.strip(), text.strip()

