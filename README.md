# Huntress/Axcient/NinjaRMM Sync Project

**Version:** 1.0.0  
**Author:** Anthony George  
**Company:** Media Managed  
**Website:** https://mediamanaged.com

## Overview

This project synchronizes data between Huntress security monitoring, Axcient x360Recover backup platform, and NinjaRMM endpoint management system. It pulls agent/device information from Huntress and Axcient, matches them to devices in NinjaRMM, and updates custom fields with status information.

## Project Structure

```
sync_project_clean/
├── sync2Ninja.py              # Main entry point
├── mm_sync/                   # Core module
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── secrets.py.template    # Template for API credentials
│   ├── utils.py               # Utility functions (logging)
│   ├── huntress.py            # Huntress API integration
│   ├── axcient.py             # Axcient x360Recover API integration
│   ├── ninja_api.py           # NinjaRMM API integration
│   ├── matching.py            # Device matching logic
│   ├── huntress_cache/        # Cached Huntress data
│   ├── axcient_cache/         # Cached Axcient data
│   └── ninja_cache/           # Cached NinjaRMM data
└── README.md                  # This file
```

## Setup

1. **Configure Secrets:**
   ```bash
   cd mm_sync
   cp secrets.py.template secrets.py
   # Edit secrets.py with your actual API credentials
   ```

2. **Install Dependencies:**
   ```bash
   pip install requests
   # Add any other dependencies as needed
   ```

3. **Run the Sync:**
   ```bash
   python3 sync2Ninja.py
   ```

## How It Works

1. **Huntress Integration:**
   - Pulls agent data and organization information from Huntress
   - Enriches agent data with organization details
   - Generates HTML status for each agent

2. **Axcient Integration:**
   - Pulls device/backup information from x360Recover
   - Generates HTML status for each backup device

3. **Device Matching:**
   - Builds maps of NinjaRMM devices by display name, DNS name, and system name
   - Matches Huntress agents and Axcient devices to NinjaRMM devices

4. **NinjaRMM Updates:**
   - Updates `huntressStatus` custom field with Huntress agent information
   - Updates `backupStatus` custom field with Axcient backup information

## Cache Files

The project maintains cache files in JSON format to reduce API calls:
- `huntress_cache/agents.json` - Huntress agent data
- `huntress_cache/orgs.json` - Huntress organization data
- `axcient_cache/devices.json` - Axcient device data
- `ninja_cache/devices.json` - NinjaRMM device inventory

Timestamp files track when data was last refreshed.

## Logging

Logs are written to the path specified in `config.py` (typically `sync.log`).

## Security Notes

- **Never commit `secrets.py`** to version control
- Add `secrets.py` to `.gitignore`
- Rotate API credentials regularly
- Use read-only credentials where possible

## Support

For issues or questions, contact:
- Anthony George
- Media Managed
- https://mediamanaged.com
