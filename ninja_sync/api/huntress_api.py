# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import base64
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
        url = f"{self.base}/v1/agents"
        limit = 100
        next_token = None
        all_agents = []

        while True:
            params = {"limit": limit}
            if next_token:
                params["page_token"] = next_token

            resp = requests.get(url, headers=self.headers(), params=params, timeout=20)

            if resp.status_code != 200:
                warn(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
                return all_agents  # soft fail

            data = resp.json()
            batch = data.get("agents", [])

            all_agents.extend(batch)

            next_token = data.get("page_info", {}).get("next_page_token")

            if not next_token:
                break

        return all_agents


    def get_orgs(self):
        url = f"{self.base}/v1/organizations"
        limit = 100
        next_token = None
        all_orgs = []

        while True:
            params = {"limit": limit}
            if next_token:
                params["page_token"] = next_token

            resp = requests.get(url, headers=self.headers(), params=params, timeout=20)

            if resp.status_code != 200:
                warn(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
                return all_orgs  # soft fail

            data = resp.json()
            batch = data.get("organizations", [])

            all_orgs.extend(batch)

            next_token = data.get("page_info", {}).get("next_page_token")

            if not next_token:
                break

        return all_orgs

