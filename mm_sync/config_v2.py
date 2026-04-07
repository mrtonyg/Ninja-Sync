"""
Configuration Settings (Streamlined)
Version: 2.0.0
Purpose: Central configuration for cache directories, TTLs, and logging paths
Usage: Imported by all mm_sync modules
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com

Changes in v2.0.0:
- Unified cache TTL (all sources use same timeout)
- Added configurable rate limiting
- Environment variable support for log path
- Auto-create cache directories if missing
"""
import os

# ===========================================================
# PATH BASE
# ===========================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ===========================================================
# CACHE CONFIGURATION
# ===========================================================
# Cache directories
HUNTRESS_CACHE_DIR = os.path.join(BASE_DIR, "huntress_cache")
NINJA_CACHE_DIR    = os.path.join(BASE_DIR, "ninja_cache")
AXCIENT_CACHE_DIR  = os.path.join(BASE_DIR, "axcient_cache")

# Unified cache TTL (seconds) - applies to all sources
CACHE_TTL = int(os.getenv("SYNC_CACHE_TTL", 60 * 30))  # Default: 30 minutes

# Legacy compatibility (for existing code)
CACHE_TTL_HUNTRESS = CACHE_TTL
CACHE_TTL_NINJA    = CACHE_TTL
CACHE_TTL_AXCIENT  = CACHE_TTL

# Auto-create cache directories
for cache_dir in [HUNTRESS_CACHE_DIR, NINJA_CACHE_DIR, AXCIENT_CACHE_DIR]:
    os.makedirs(cache_dir, exist_ok=True)

# ===========================================================
# LOGGING CONFIGURATION
# ===========================================================
# Log path (environment variable override supported)
LOG_PATH = os.getenv("SYNC_LOG_PATH", "/var/log/sync2Ninja.log")

# Fallback to local log if /var/log is not writable
if not os.access(os.path.dirname(LOG_PATH), os.W_OK):
    LOG_PATH = os.path.join(BASE_DIR, "..", "sync.log")

# ===========================================================
# API RATE LIMITING
# ===========================================================
# Delay between NinjaRMM API updates (seconds)
NINJA_UPDATE_DELAY = float(os.getenv("NINJA_UPDATE_DELAY", 0.1))

# ===========================================================
# PARALLEL PROCESSING
# ===========================================================
# Maximum concurrent workers for parallel sync
MAX_WORKERS = int(os.getenv("SYNC_MAX_WORKERS", 5))
