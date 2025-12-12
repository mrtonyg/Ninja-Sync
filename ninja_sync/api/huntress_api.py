# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import requests
from ..core.logger import warn
from ..core.utils import make_basic_auth
from ..core import config
from ..core.secrets import HUNTRESS_PUBLIC_KEY, HUNTRESS_PRIVATE_KEY

class HuntressAPI:
    def __init__(self):
        #key = make_basic_auth(HUNTRESS_PUBLIC_KEY, HUNTRESS_PRIVATE_KEY)
        #self.headers = {"Authorization": f"Basic {key}"}
        raw = f"{HUNTRESS_PUBLIC_KEY}:{HUNTRESS_PRIVATE_KEY}"
        token = base64.b64encode(raw.encode("utf-8")).decode("utf-8")
        self.headers = {
            "Authorization": f"Basic {token}",
            "Accept": "application/json"
        }

    def get_agents(self):
        url = f"{config.HUNTRESS_BASE_URL}/agents"
        agents = []
        page = 1

        while True:
            resp = requests.get(url, headers=self.headers, params={"page": page})
            if resp.status_code != 200:
                warn(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
                break

            data = resp.json()
            chunk = data.get("agents", [])
            agents.extend(chunk)

            if not data.get("pagination", {}).get("has_next_page"):
                break
            page += 1

        return agents

    def get_orgs(self):
        url = f"{config.HUNTRESS_BASE_URL}/organizations"
        orgs = []
        page = 1

        while True:
            resp = requests.get(url, headers=self.headers, params={"page": page})
            if resp.status_code != 200:
                warn(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
                break

            data = resp.json()
            chunk = data.get("organizations", [])
            orgs.extend(chunk)

            if not data.get("pagination", {}).get("has_next_page"):
                break
            page += 1

        return orgs
