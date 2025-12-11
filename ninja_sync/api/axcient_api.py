# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import requests
from ..core.logger import warn
from ..core import config
from ..core.secrets import AXCIENT_API_KEY

class AxcientAPI:
    def __init__(self):
        self.headers = {"X-Api-Key": AXCIENT_API_KEY}

    def get_devices(self):
        url = f"{config.AXCIENT_BASE_URL}/device"
        devices = []
        offset = 0
        limit = 100

        while True:
            resp = requests.get(url, headers=self.headers,
                                params={"limit": limit, "offset": offset})
            if resp.status_code != 200:
                warn(f"Axcient GET failed {url}: {resp.status_code} {resp.text}")
                break

            batch = resp.json()
            if not isinstance(batch, list):
                warn("Axcient response unexpected (not list)")
                break

            devices.extend(batch)

            if len(batch) < limit:
                break

            offset += limit

        return devices
