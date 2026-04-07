"""
Common API Utilities
Version: 2.0.0
Purpose: Shared caching logic and API helpers to reduce code duplication
Usage: Imported by huntress.py, axcient.py, ninja_api.py
Author: Anthony George
Company: Media Managed
Website: https://mediamanaged.com

New in v2.0.0:
- Generic caching functions to eliminate duplicate cache logic
- Retry logic with exponential backoff
- Standardized API error handling
"""
import json
import os
import time
import requests
from functools import wraps

from .utils import log, log_error


class CacheManager:
    """Generic cache manager for API responses."""
    
    def __init__(self, cache_dir, ttl_seconds):
        self.cache_dir = cache_dir
        self.ttl = ttl_seconds
        self.data_file = os.path.join(cache_dir, "data.json")
        self.timestamp_file = os.path.join(cache_dir, "timestamp.json")
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
    
    def is_valid(self):
        """Check if cache is still valid based on TTL."""
        try:
            with open(self.timestamp_file, "r") as f:
                ts = json.load(f)["timestamp"]
            return (time.time() - ts) < self.ttl
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False
    
    def read(self):
        """Read cached data."""
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def write(self, data):
        """Write data to cache with timestamp."""
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
            
            with open(self.timestamp_file, "w") as f:
                json.dump({"timestamp": time.time()}, f)
            
            log(f"[CACHE] Wrote cache to {self.cache_dir}")
        except Exception as e:
            log_error(f"Failed to write cache: {e}")
    
    def get_or_fetch(self, fetch_func):
        """
        Get data from cache if valid, otherwise fetch fresh data.
        
        Args:
            fetch_func: Callable that returns fresh data
        
        Returns:
            Cached or fresh data
        """
        if self.is_valid():
            log(f"[CACHE] Using cached data from {self.cache_dir}")
            data = self.read()
            if data is not None:
                return data
        
        log(f"[CACHE] Cache miss or expired, fetching fresh data...")
        data = fetch_func()
        self.write(data)
        return data


def retry_on_failure(max_retries=3, backoff_factor=2):
    """
    Decorator to retry API calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for wait time between retries
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    wait_time = backoff_factor ** attempt
                    if attempt < max_retries - 1:
                        log(f"[RETRY] Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        log_error(f"All {max_retries} attempts failed for {func.__name__}")
                        raise
            return None
        return wrapper
    return decorator


def make_api_request(url, method="GET", headers=None, params=None, json_data=None, auth=None):
    """
    Standardized API request with error handling.
    
    Args:
        url: API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE)
        headers: Request headers dict
        params: URL parameters dict
        json_data: JSON body for POST/PUT requests
        auth: Authentication tuple (username, password)
    
    Returns:
        Response JSON or raises exception
    """
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            auth=auth,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    except requests.HTTPError as e:
        log_error(f"HTTP Error: {e.response.status_code}", url=url, response=e.response)
        raise
    except requests.RequestException as e:
        log_error(f"Request failed: {e}", url=url)
        raise
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON response: {e}", url=url)
        raise
