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
        url = f"{config.HUNTRESS_BASE_URL}/v1/agents"
        page = 1
        all_agents = []

        while True:
            resp = requests.get(
                f"{url}?page={page}",
                headers=self.headers(),
                timeout=15
            )

            if resp.status_code != 200:
                warn(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
                return all_agents  # soft fail

            data = resp.json()
            batch = data.get("agents", [])

            if not batch:
                break

            all_agents.extend(batch)

            # Stop if we received fewer than the page size (default = 100)
            if len(batch) < 100:
                break

            page += 1

    return all_agents

    def get_orgs(self):
        url = f"{config.HUNTRESS_BASE_URL}/v1/organizations"
        page = 1
        all_orgs = []

        while True:
            resp = requests.get(
                f"{url}?page={page}",
                headers=self.headers(),
                timeout=15
            )

            if resp.status_code != 200:
                warn(f"Huntress GET failed {url}: {resp.status_code} {resp.text}")
                return all_orgs  # soft fail

            data = resp.json()
            batch = data.get("organizations", [])

            if not batch:
                break

            all_orgs.extend(batch)

            if len(batch) < 100:
                break

            page += 1

        return all_orgs

