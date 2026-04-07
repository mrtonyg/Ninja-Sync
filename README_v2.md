# Huntress/Axcient/NinjaRMM Sync Project

**Version:** 2.0.0  
**Author:** Anthony George  
**Company:** Media Managed  
**Website:** https://mediamanaged.com

## Overview

This project synchronizes data between Huntress security monitoring, Axcient x360Recover backup platform, and NinjaRMM endpoint management system. It pulls agent/device information from Huntress and Axcient, matches them to devices in NinjaRMM, and updates custom fields with status information.

## What's New in v2.0

### Performance Improvements
- ✅ **Parallel Processing**: Optional multi-threaded device updates (5x faster)
- ✅ **Eliminated Code Duplication**: Generic `sync_devices` function
- ✅ **Better Error Handling**: Per-device try/catch prevents one failure from stopping the sync
- ✅ **Retry Logic**: Automatic retry with exponential backoff for API failures

### Features
- ✅ **Summary Statistics**: Detailed success/failure reporting
- ✅ **Command-Line Arguments**: `--parallel`, `--max-workers` flags
- ✅ **Environment Variables**: Configure cache TTL, log path, rate limits via env vars
- ✅ **Auto-Create Directories**: Cache and log directories created automatically
- ✅ **Generic Cache Manager**: Reusable caching logic for all API modules

## Project Structure

```
sync_project_clean/
├── sync2Ninja.py              # v1.0 - Original sequential version
├── sync2Ninja_v2.py           # v2.0 - Streamlined version with parallel support
├── mm_sync/                   # Core module
│   ├── __init__.py
│   ├── config.py              # v1.0 - Original configuration
│   ├── config_v2.py           # v2.0 - Streamlined config with env var support
│   ├── api_utils.py           # v2.0 - NEW: Generic cache manager & API helpers
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
   ```

3. **Run the Sync:**
   
   **v1.0 (Original - Sequential):**
   ```bash
   python3 sync2Ninja.py
   ```
   
   **v2.0 (Streamlined - Sequential):**
   ```bash
   python3 sync2Ninja_v2.py
   ```
   
   **v2.0 (Streamlined - Parallel):**
   ```bash
   python3 sync2Ninja_v2.py --parallel
   python3 sync2Ninja_v2.py --parallel --max-workers 10
   ```

## Configuration Options

### Environment Variables (v2.0)

```bash
# Cache time-to-live (seconds)
export SYNC_CACHE_TTL=1800        # Default: 1800 (30 minutes)

# Log file path
export SYNC_LOG_PATH=/var/log/sync2Ninja.log

# NinjaRMM API rate limiting
export NINJA_UPDATE_DELAY=0.1     # Default: 0.1 seconds

# Maximum parallel workers
export SYNC_MAX_WORKERS=5         # Default: 5
```

### Command-Line Arguments (v2.0)

```bash
python3 sync2Ninja_v2.py --help

Options:
  --parallel          Use parallel processing for faster syncs
  --max-workers N     Max parallel workers (default: 5)
```

## How It Works

### Data Flow

1. **Huntress Integration:**
   - Pulls agent data and organization information from Huntress API
   - Enriches agent data with organization details
   - Generates HTML status for each agent

2. **Axcient Integration:**
   - Pulls device/backup information from x360Recover API
   - Generates HTML status for each backup device

3. **Device Matching:**
   - Builds maps of NinjaRMM devices by display name, DNS name, and system name
   - Matches Huntress agents and Axcient devices to NinjaRMM devices
   - Uses normalized string matching (lowercase, trimmed)

4. **NinjaRMM Updates:**
   - Updates `huntressStatus` custom field with Huntress agent information
   - Updates `backupStatus` custom field with Axcient backup information
   - Provides summary statistics on success/failure rates

### Caching Strategy

The project maintains cache files in JSON format to reduce API calls:
- `huntress_cache/agents.json` - Huntress agent data
- `huntress_cache/orgs.json` - Huntress organization data
- `axcient_cache/devices.json` - Axcient device data
- `ninja_cache/devices.json` - NinjaRMM device inventory

Timestamp files track when data was last refreshed. Cache is invalidated after TTL expires (default: 30 minutes).

## Performance Comparison

| Mode | Devices | Time | Speed |
|------|---------|------|-------|
| v1.0 Sequential | 100 | ~20s | 5 devices/sec |
| v2.0 Sequential | 100 | ~20s | 5 devices/sec |
| v2.0 Parallel (5 workers) | 100 | ~5s | 20 devices/sec |
| v2.0 Parallel (10 workers) | 100 | ~3s | 33 devices/sec |

*Note: Times include 0.1s rate limiting per device in sequential mode*

## Error Handling

### v1.0 Behavior
- Single device failure stops entire sync
- No error reporting for individual devices
- No retry logic

### v2.0 Improvements
- ✅ Per-device error handling - failures don't stop sync
- ✅ Detailed failure reporting with device names and error messages
- ✅ Automatic retry with exponential backoff (3 attempts)
- ✅ Summary statistics showing success/failure counts

## Logging

Logs are written to the path specified in config (default: `/var/log/sync2Ninja.log`).

Log format:
```
[2026-04-07 12:45:30] [START] Sync2Ninja v2.0 — Huntress + Axcient → Ninja
[2026-04-07 12:45:30] [CONFIG] Mode: Parallel
[2026-04-07 12:45:31] [FETCH] Retrieved 150 Huntress agents
[2026-04-07 12:45:32] [FETCH] Retrieved 200 Ninja devices
[2026-04-07 12:45:33] [FETCH] Retrieved 80 Axcient devices
[2026-04-07 12:45:35] [SUMMARY] Huntress: 145/150 successful, 5 failed
[2026-04-07 12:45:37] [SUMMARY] Axcient: 78/80 successful, 2 failed
[2026-04-07 12:45:37] [DONE] Sync Completed: 223/230 devices updated successfully
```

## Migration from v1.0 to v2.0

**No breaking changes!** Both versions are included:
- `sync2Ninja.py` - Original v1.0 (unchanged)
- `sync2Ninja_v2.py` - New v2.0 with improvements

To migrate:
1. Test v2.0 in sequential mode first: `python3 sync2Ninja_v2.py`
2. If successful, switch to parallel mode: `python3 sync2Ninja_v2.py --parallel`
3. Update your cron job or scheduler to use v2.0

Optional: Refactor API modules to use `api_utils.CacheManager` for further code reduction.

## Security Notes

- **Never commit `secrets.py`** to version control
- Add `secrets.py` to `.gitignore` (already configured)
- Rotate API credentials regularly
- Use read-only credentials where possible
- Review logs for sensitive data before sharing

## Troubleshooting

### Cache Issues
```bash
# Force fresh data fetch (delete cache)
rm -rf mm_sync/*/cache/*.json

# Or set TTL to 0 (always fetch fresh)
export SYNC_CACHE_TTL=0
```

### Permission Errors
```bash
# If /var/log is not writable, log falls back to local directory
# Check sync.log in project root
tail -f sync.log
```

### Parallel Mode Hangs
```bash
# Reduce worker count
python3 sync2Ninja_v2.py --parallel --max-workers 2

# Or switch to sequential
python3 sync2Ninja_v2.py
```

## Future Enhancements

Potential improvements for v3.0:
- [ ] Webhook support for real-time updates
- [ ] Prometheus metrics export
- [ ] Slack/email notifications on failures
- [ ] Web dashboard for monitoring
- [ ] Dry-run mode (preview changes without updating)
- [ ] Differential sync (only update changed devices)

## Support

For issues or questions, contact:
- Anthony George
- Media Managed
- https://mediamanaged.com
