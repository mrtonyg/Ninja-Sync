"""
=====================================================================
  ninja_sync/core/logger.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Unified Logging Module
=====================================================================

Provides:
  - log(msg):   Standard informational logging
  - warn(msg):  Warning logging
  - error(msg): Error logging
  - debug(msg): Debug logging (enabled via config.DEBUG_MODE or CLI)
  - write_to_logfile(msg): Writes full logs to data/logs/sync.log
"""

import os
import datetime
from ninja_sync.core.config import LOG_PATH, DEBUG_MODE


# -------------------------------------------------------------------
# INTERNAL — Write plain text to log file
# -------------------------------------------------------------------
def write_to_logfile(msg: str):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        # Silent failure — logging should never stop execution
        pass


# -------------------------------------------------------------------
# Formatting helper
# -------------------------------------------------------------------
def _stamp() -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{now}]"


# -------------------------------------------------------------------
# Public logging functions
# -------------------------------------------------------------------
def log(msg: str):
    line = f"{_stamp()} [INFO] {msg}"
    print(line)
    write_to_logfile(line)


def warn(msg: str):
    line = f"{_stamp()} [WARN] {msg}"
    print(line)
    write_to_logfile(line)


def error(msg: str):
    line = f"{_stamp()} [ERROR] {msg}"
    print(line)
    write_to_logfile(line)


def debug(msg: str):
    from ninja_sync.core.config import DEBUG_MODE as _DBG
    if _DBG:
        line = f"{_stamp()} [DEBUG] {msg}"
        print(line)
        write_to_logfile(line)
