# MM_syncNinja
Unified Huntress + Axcient → NinjaOne Device Sync Engine  
Author: Anthony George (Media Managed)

## Overview
`MM_syncNinja` is a modular Python-based synchronization system designed to pull
endpoint details from:

- **Huntress** (EDR + agent status)
- **Axcient x360Recover** (backup & AutoVerify status)
- **NinjaOne v2 API** (device inventory + custom fields)

It resolves device names across different systems, generates WYSIWYG-safe HTML
summaries, and updates two NinjaOne custom fields:

- `huntressStatus`
- `backupStatus`

The project uses a full modular architecture with caching, OAuth2, pagination,
logging, error handling, and selective cache clearing.

MM_syncNinja/
│
├── sync2Ninja.py # Main orchestrator
└── mm_sync/
├── config.py # Cache paths, TTLs, log location
├── secrets.py # API keys (placeholders)
├── utils.py # Logging, JSON helpers, cache clearing
├── huntress.py # Huntress integration + HTML builder
├── axcient.py # Axcient integration + HTML builder
├── ninja_api.py # NinjaOne OAuth2, devices, custom fields
├── matching.py # Device matching logic
└── init.py


---

## Features

### ✔ Huntress Integration
- Pulls `/agents` and `/organizations`  
- Pagination-aware  
- Caches for 30 minutes  
- Maps `organization_id` → org name  
- WYSIWYG-safe summary HTML  
- Includes Defender status, firewall state, EDR version, updated_at, and more  

### ✔ Axcient Integration
- Uses `/device` (singular endpoint)
- Correct pagination (`limit`, `offset`)
- Handles raw list or wrapped object responses
- Includes:
  - AutoVerify details (status + timestamp)
  - Latest Cloud Recovery Point
  - Current Health Status (inline timestamp)
  - Agent Version
- WYSIWYG-safe HTML summary  

### ✔ NinjaOne Integration
- Full OAuth2 “client credentials” flow
- Token caching with expiration tracking
- Pulls devices via v2 API (`/v2/devices`)
- Updates WYSIWYG custom fields:
  - `huntressStatus`
  - `backupStatus`
- Resilient error handling & detailed logging

### ✔ Device Matching
Matches devices across systems using:

1. `displayName`
2. `dnsName`
3. `systemName`
4. Stripped hostname (FQDN → hostname)

### ✔ Selective Cache Clearing
Available command-line flags:

--clear-axcient
--clear-ninja
--clear-all
--clear-cache # interactive menu


### ✔ Logging
Logs to:

sync2Ninja.log


Includes timestamps, API errors, update results, and cache events.

---

## Installation

### 1. Clone the project


git clone https://github.com/YOUR_REPO/MM_syncNinja.git

cd MM_syncNinja


### 2. Install dependencies
Requires Python 3.8+.

Install `requests`:


pip3 install requests


### 3. Edit the API secrets
Open:


mm_sync/secrets.py


Replace placeholders:
```python
HUNTRESS_KEY = "YOUR_HUNTRESS_KEY"
HUNTRESS_SECRET = "YOUR_HUNTRESS_SECRET"

AXCIENT_API_KEY = "YOUR_AXCIENT_API_KEY"

NINJA_CLIENT_ID = "YOUR_NINJA_CLIENT_ID"
NINJA_CLIENT_SECRET = "YOUR_NINJA_CLIENT_SECRET"

Usage
Run normally:
./sync2Ninja.py

Clear all caches:
./sync2Ninja.py --clear-all

Clear one cache:
./sync2Ninja.py --clear-huntress
./sync2Ninja.py --clear-axcient
./sync2Ninja.py --clear-ninja

Interactive cache clearing:
./sync2Ninja.py --clear-cache

Cron Example

Update every 30 minutes:

*/30 * * * * /usr/bin/python3 /root/MM_syncNinja/sync2Ninja.py >> /root/MM_syncNinja/cron.log 2>&1

Custom Fields Required in NinjaOne

Create these rich text custom fields:

huntressStatus
backupStatus


Type:

“This text field allows for text with bold, italic, underline, hyperlinks, etc.”

Troubleshooting
HTML formatting looks wrong

NinjaOne sanitizes aggressively.
This project uses only:

<p>

<b>

<u>

text and emojis

These remain intact.

Device not matched

Ensure names match:

Huntress hostname

Axcient name

NinjaOne displayName, dnsName, systemName

Axcient paging issues

Ensure:

limit ≤ 200

offset increments by limit

This project handles that automatically.

Future Enhancements

Slack/Teams alerting

Backup RP age thresholds

Automatic indepth health scoring

Huntress incident count integration

NinjaOne UI “force refresh” toggle

License

Internal use only — Media Managed.
Do not distribute externally.