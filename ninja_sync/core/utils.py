"""
Media Managed — Ninja Sync Utilities
Version: 2.0.9
Author: Anthony George
"""

import base64
import re
import json
from datetime import datetime


# -------------------------------------------------------------
# Logging helpers
# -------------------------------------------------------------
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    print(f"[{now()}] [INFO] {msg}")


def warn(msg):
    print(f"[{now()}] [WARN] {msg}")


def error(msg):
    print(f"[{now()}] [ERROR] {msg}")


# -------------------------------------------------------------
# HTML helpers
# -------------------------------------------------------------
HTML_TAG_RE = re.compile(r"<[^>]+>")

def strip_html(html: str) -> str:
    """
    Remove all HTML tags using regex. Safe for our specific usage where the
    HTML is fully controlled and not user-generated.
    """
    if not html:
        return ""
    # Remove tags
    text = HTML_TAG_RE.sub("", html)
    # Normalize whitespace
    text = " ".join(text.split())
    return text.strip()


# -------------------------------------------------------------
# Authentication helpers
# -------------------------------------------------------------
def make_basic_auth(public_key, private_key):
    """
    Huntress requires: base64("public:private")
    """
    token = f"{public_key}:{private_key}".encode("utf-8")
    b64 = base64.b64encode(token).decode("utf-8")
    return f"Basic {b64}"


# -------------------------------------------------------------
# JSON pretty
# -------------------------------------------------------------
def pretty_json(obj):
    try:
        return json.dumps(obj, indent=2)
    except Exception:
        return str(obj)
