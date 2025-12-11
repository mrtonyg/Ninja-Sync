# Media Managed – Ninja-Sync
# Version: 2.0.9
# Author: Anthony George

import datetime

def ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def info(msg):
    print(f"[{ts()}] [INFO] {msg}")

def warn(msg):
    print(f"[{ts()}] [WARN] {msg}")

def error(msg):
    print(f"[{ts()}] [ERROR] {msg}")
