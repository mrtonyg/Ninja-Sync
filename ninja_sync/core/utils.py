"""
=====================================================================
  ninja_sync/core/utils.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Utility Functions
=====================================================================

Includes:
  - base64_basic_auth(user, pwd)
  - strip_html(html)
  - safe_get(d, *keys)   ← nested dict accessor
"""

import base64
import re
from html import unescape


# -------------------------------------------------------------------
# Build Huntress Basic Auth header
# -------------------------------------------------------------------
def base64_basic_auth(public_key: str, private_key: str) -> str:
    token = f"{public_key}:{private_key}".encode("utf-8")
    return base64.b64encode(token).decode("utf-8")


# -------------------------------------------------------------------
# Strip HTML → plain text (for Ninja WYSIWYG `.text` field)
# -------------------------------------------------------------------
def strip_html(html: str) -> str:
    if not html:
        return ""
    # Remove tags
    text = re.sub(r"<[^>]*>", "", html)
    # Decode HTML entities
    text = unescape(text)
    # Trim whitespace
    return text.strip()


# -------------------------------------------------------------------
# Safe nested getter: safe_get(obj, "a", "b", "c")
# -------------------------------------------------------------------
def safe_get(data, *keys):
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
        if data is None:
            return None
    return data
