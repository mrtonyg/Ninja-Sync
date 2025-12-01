# config.py
# Central configuration for cache directories, TTLs, and log paths.

import os

# Base directory (auto-detects current file location)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

# -------------------------------------------------------------------
# Cache Directories
# -------------------------------------------------------------------
HUNTRESS_CACHE_DIR = os.path.join(ROOT_DIR, "cache_huntress")
AXCIENT_CACHE_DIR  = os.path.join(ROOT_DIR, "cache_axcient")
NINJA_CACHE_DIR    = os.path.join(ROOT_DIR, "cache_ninja")

# Ensure directories exist when modules import this config
for d in [HUNTRESS_CACHE_DIR, AXCIENT_CACHE_DIR, NINJA_CACHE_DIR]:
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)

# -------------------------------------------------------------------
# Cache Expiration Times (in seconds)
# -------------------------------------------------------------------
CACHE_TTL_HUNTRESS = 30 * 60    # 30 minutes
CACHE_TTL_AXCIENT  = 30 * 60    # 30 minutes
CACHE_TTL_NINJA    = 30 * 60    # 30 minutes

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
LOG_PATH = os.path.join(ROOT_DIR, "sync2Ninja.log")

