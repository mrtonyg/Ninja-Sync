"""
Configuration Settings
Version: 1.0.0
Purpose: Central configuration for cache directories, TTLs, and logging paths
Usage: Imported by all mm_sync modules
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com
"""
import os

# ===========================================================
# PATH BASE
# ===========================================================
# Default: current directory + /mm-sync
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Cache directories (all customizable)
HUNTRESS_CACHE_DIR = os.path.join(BASE_DIR, "huntress_cache")
NINJA_CACHE_DIR    = os.path.join(BASE_DIR, "ninja_cache")
AXCIENT_CACHE_DIR  = os.path.join(BASE_DIR, "axcient_cache")

# Cache TTLs
CACHE_TTL_HUNTRESS = 60 * 30      # 30 minutes
CACHE_TTL_NINJA    = 60 * 30
CACHE_TTL_AXCIENT  = 60 * 30

# Logging
LOG_PATH = "/var/log/sync2Ninja.log"
