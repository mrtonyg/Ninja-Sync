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
        self.base = config.HUNTRESS_BASE_URL
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
        limit = 50
        token = None
        all_agents = []

        while True:
            params = {"limit": limit}
            if token:
                params["page_token"] = token

            resp = requests.get(url, headers=self.headers(), params=params, timeout=20)

            if resp.status_code != 200:
                warn(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
                return all_agents  # soft fail to allow sync to continue

            data = resp.json()

            agents = data.get("agents", [])
            pagination = data.get("pagination", {})

            all_agents.extend(agents)

            token = pagination.get("next_page_token")

            if not token:
                break

        return all_agents



    def get_orgs(self):
        url = f"{self.base}/v1/organizations"
        limit = 50
        token = None
        all_orgs = []

        while True:
            params = {"limit": limit}
            if token:
                params["page_token"] = token

            resp = requests.get(url, headers=self.headers(), params=params, timeout=20)

            if resp.status_code != 200:
                warn(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
                return all_orgs

            data = resp.json()

            orgs = data.get("organizations", [])
            pagination = data.get("pagination", {})

            all_orgs.extend(orgs)

            token = pagination.get("next_page_token")

            if not token:
                break

        return all_orgs


