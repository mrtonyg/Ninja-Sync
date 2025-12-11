"""
html_builder.py
Version: 2.0.2
Author: Anthony George

Purpose:
    Provides formatted WYSIWYG-safe output blocks for NinjaOne custom fields.
    Output uses aligned monospace-style spacing because Ninja strips <table>,
    inline CSS, spans, and most other markup.

Supports:
    - Huntress agent status formatting
    - Axcient backup device status formatting
"""

# -------------------------------------------------------------------------
# Utility: pad fields for clean aligned output
# -------------------------------------------------------------------------
def align(label, value, width=20):
    """
    Produces consistent, readable output in NinjaOne's WYSIWYG text field.
    """
    label_block = f"{label}:".ljust(width)
    return f"{label_block}{value}"


# -------------------------------------------------------------------------
# Huntress Section Builder
# -------------------------------------------------------------------------
def build_huntress_section(agent, org_name):
    """
    agent: Huntress agent object from pull_huntress()['agents']
    org_name: Resolved organization name for display
    """

    return (
f"""Huntress Status
----------------
{align("Device Name", agent.get("hostname", "unknown"))}
{align("Organization", org_name)}
{align("Serial Number", agent.get("serial_number", "unknown"))}
{align("Operating System", agent.get("os", "unknown"))}
{align("Platform", agent.get("platform", "unknown"))}
{align("Internal IP", agent.get("ipv4_address", "unknown"))}
{align("External IP", agent.get("external_ip", "unknown"))}

Times
{align("Last Callback", agent.get("last_callback_at", "unknown"))}
{align("Last Survey", agent.get("last_survey_at", "unknown"))}
{align("Updated At", agent.get("updated_at", "unknown"))}

Versions
{align("Agent Version", agent.get("version", "unknown"))}
{align("EDR Version", agent.get("edr_version", "unknown"))}

Status
{align("Defender Status", agent.get("defender_status", "unknown"))}
{align("Defender Substatus", agent.get("defender_substatus", "unknown"))}
{align("Policy Status", agent.get("defender_policy_status", "unknown"))}
{align("Firewall Status", agent.get("firewall_status", "unknown"))}
""").strip()


# -------------------------------------------------------------------------
# Axcient Backup Section Builder
# -------------------------------------------------------------------------
def build_axcient_section(dev):
    """
    dev: Axcient device object from pull_axcient()
    """

    chs = dev.get("current_health_status", {})
    av = dev.get("latest_autoverify_details", {})

    current_status = chs.get("status", "unknown")
    current_ts = chs.get("timestamp", "unknown")

    av_status = av.get("status", "unknown")
    av_ts = av.get("timestamp", "unknown")

    cloud_rp = dev.get("latest_cloud_rp", "unknown")

    return (
f"""Backup Status
--------------
{align("Device Name", dev.get("name", "unknown"))}
{align("Current Status", f"{current_status} ({current_ts})")}
{align("AutoVerify", f"{av_status} ({av_ts})")}
{align("Latest Cloud RP", cloud_rp)}
{align("Agent Version", dev.get("agent_version", "unknown"))}
""").strip()

