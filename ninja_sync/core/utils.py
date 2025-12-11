# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import base64
from bs4 import BeautifulSoup  # ensure bs4 is installed

def make_basic_auth(user, pw):
    raw = f"{user}:{pw}".encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")

def strip_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)
