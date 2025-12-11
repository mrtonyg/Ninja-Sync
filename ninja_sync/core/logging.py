"""
==============================================================
  ninja_sync/core/logging.py
  Ninja-Sync v2.0.8
  Media Managed — Anthony George
  Logging utilities
==============================================================
"""

import json
import datetime


def _ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    print(f"[{_ts()}] [INFO] {msg}")


def warn(msg):
    print(f"[{_ts()}] [WARN] {msg}")


def error(msg, url=None, params=None, resp=None):
    print(f"[{_ts()}] [ERROR] {msg}")

    if url:
        print(f"   URL: {url}")

    if params:
        print(f"   Params: {params}")

    if resp is not None:
        try:
            body = resp.text
        except:
            body = str(resp)

        print(f"   HTTP Status: {resp.status_code}")
        print(f"   Response: {body}")

    print("")  # Spacer
