"""
Utility Functions
Version: 1.0.0
Purpose: Logging, text normalization, and error handling utilities
Usage: Imported by all mm_sync modules for logging and string operations
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com
"""
import datetime
import re
import traceback

from .config import LOG_PATH

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except:
        pass

def log_error(message, url=None, params=None, response=None):
    log(f"[ERROR] {message}")
    if url: log(f" URL: {url}")
    if params: log(f" Params: {params}")
    if response is not None:
        log(f" HTTP: {response.status_code}")
        log(f" BODY: {response.text}")
    log(traceback.format_exc())

def strip_html(html):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)

def norm(s):
    if not s:
        return ""
    return str(s).strip().lower()
