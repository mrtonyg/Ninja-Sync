"""
matching.py
Version: 2.0.1
Author: Anthony George
"""

def glyph(status):
    if not status:
        return "⚪"
    status = status.lower()
    if "normal" in status or "protected" in status or "success" in status:
        return "🟢"
    if "warn" in status:
        return "🟡"
    return "🔴"

def line(label, value):
    return f"<b>{label}:</b> {value}<br>"

def section(title):
    return f"<h3>{title}</h3>"

def build_huntress_html(agent, org):
    html = section("Huntress Status")

    html += line("Device", agent.get("hostname"))
    html += line("Organization", org)
    html += line("Serial", agent.get("serial_number"))
    html += line("OS", agent.get("os"))
    html += line("Platform", agent.get("platform"))
    html += line("Internal IP", agent.get("ipv4_address"))
    html += line("External IP", agent.get("external_ip"))
    html += line("Last Callback", agent.get("last_callback_at"))
    html += line("Last Survey", agent.get("last_survey_at"))
    html += line("Agent Version", agent.get("version"))
    html += line("EDR Version", agent.get("edr_version"))
    html += "<br>"

    html += line("Defender Status", f"{glyph(agent.get('defender_status'))} {agent.get('defender_status')}")
    html += line("Defender Substatus", f"{glyph(agent.get('defender_substatus'))} {agent.get('defender_substatus')}")
    html += line("Defender Policy", f"{glyph(agent.get('defender_policy_status'))} {agent.get('defender_policy_status')}")
    html += line("Firewall Status", f"{glyph(agent.get('firewall_status'))} {agent.get('firewall_status')}")
    return html

def build_axcient_html(d):
    html = section("Backup Status")

    html += line("Device", d.get("name"))
    stat = d.get("current_health_status", {})
    html += line("Current Status", f"{glyph(stat.get('status'))} {stat.get('status')}")
    html += line("Status Time", stat.get("timestamp"))

    av = d.get("latest_autoverify_details")
    if av:
        html += line("AutoVerify", f"{glyph(av.get('status'))} {av.get('status')}")
        html += line("AutoVerify Time", av.get("timestamp"))

    html += line("Agent Version", d.get("agent_version"))
    html += line("Latest Cloud RP", d.get("latest_cloud_rp"))
    return html
