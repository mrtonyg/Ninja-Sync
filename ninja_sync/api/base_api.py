# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import requests
from ..core.logger import warn, error

class BaseAPI:
    def get(self, url, headers=None, params=None):
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code not in (200, 201):
            warn(f"GET failed {url}: {resp.status_code} {resp.text}")
            return None
        return resp.json()
