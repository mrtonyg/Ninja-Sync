# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import requests
from ..core.logger import warn, info, error
from ..core.utils import strip_html
from ..core import config
from ..core.secrets import NINJA_CLIENT_ID, NINJA_CLIENT_SECRET

class NinjaAPI:
    def __init__(self):
        self.token = None

    def authenticate(self):
        url = f"{config.NINJA_BASE_URL}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": NINJA_CLIENT_ID,
            "client_secret": NINJA_CLIENT_SECRET,
            "scope": "monitoring management control"
        }

        resp = requests.post(url, data=payload)
        if resp.status_code != 200:
            error(f"Ninja token error: {resp.status_code} {resp.text}")
            return False

        self.token = resp.json().get("access_token")
        return True

    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def get_devices(self):
        url = f"{config.NINJA_BASE_URL}/v2/devices"
        resp = requests.get(url, headers=self.headers())

        if resp.status_code != 200:
            error(f"Ninja devices fetch error: {resp.status_code} {resp.text}")
            return []
        return resp.json()

    def update_custom_field(self, device_id, field_name, html):
        url = f"{config.NINJA_BASE_URL}/v2/device/{device_id}/custom-fields"

        payload = {
            field_name: {
                "text": strip_html(html),
                "html": html
            }
        }

        resp = requests.patch(url, headers=self.headers(), json=payload)
        if resp.status_code not in (200, 204):
            warn(f"Failed updating custom field {field_name}: {resp.status_code} {resp.text}")
            return False

        info(f"[OK] Updated {field_name} on device {device_id}")
        return True
