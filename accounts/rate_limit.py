"""
WorkWave Security Framework - Authentication Rate Limiting & Brute Force Defense.
Uses Django's cache abstraction to track failed login attempts by client IP and username.
"""

import time
from django.core.cache import cache

MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 300 seconds (5 minutes)


def get_client_ip(request):
    """
    Extracts client IP address safely, checking X-Forwarded-For when behind a proxy.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


def _get_cache_keys(request, username=None):
    ip = get_client_ip(request)
    normalized_ip = ip.replace(":", "_").replace(".", "_")
    ip_attempts_key = f"ww_auth_att_ip_{normalized_ip}"
    ip_lockout_key = f"ww_auth_lock_ip_{normalized_ip}"

    user_attempts_key = None
    user_lockout_key = None
    if username:
        normalized_user = username.strip().lower()
        user_attempts_key = f"ww_auth_att_usr_{normalized_user}"
        user_lockout_key = f"ww_auth_lock_usr_{normalized_user}"

    return {
        "ip_attempts_key": ip_attempts_key,
        "ip_lockout_key": ip_lockout_key,
        "user_attempts_key": user_attempts_key,
        "user_lockout_key": user_lockout_key,
    }


def is_locked_out(request, username=None):
    """
    Checks if the IP or username is currently under temporary lockout.
    Returns (is_locked: bool, remaining_seconds: int)
    """
    keys = _get_cache_keys(request, username)
    now = time.time()

    # Check IP lockout
    ip_lock_until = cache.get(keys["ip_lockout_key"])
    if ip_lock_until and ip_lock_until > now:
        return True, int(ip_lock_until - now)

    # Check User lockout
    if keys["user_lockout_key"]:
        user_lock_until = cache.get(keys["user_lockout_key"])
        if user_lock_until and user_lock_until > now:
            return True, int(user_lock_until - now)

    return False, 0


def record_failed_attempt(request, username=None):
    """
    Records a failed authentication attempt. Triggers lockout if threshold is exceeded.
    Returns (locked_now: bool, remaining_seconds: int)
    """
    keys = _get_cache_keys(request, username)
    now = time.time()
    lockout_expiry = now + LOCKOUT_DURATION

    # Record IP attempt
    ip_attempts = cache.get(keys["ip_attempts_key"], 0) + 1
    cache.set(keys["ip_attempts_key"], ip_attempts, LOCKOUT_DURATION)

    # Record User attempt
    user_attempts = 0
    if keys["user_attempts_key"]:
        user_attempts = cache.get(keys["user_attempts_key"], 0) + 1
        cache.set(keys["user_attempts_key"], user_attempts, LOCKOUT_DURATION)

    # Evaluate lockout threshold
    if ip_attempts >= MAX_ATTEMPTS:
        cache.set(keys["ip_lockout_key"], lockout_expiry, LOCKOUT_DURATION)
        return True, LOCKOUT_DURATION

    if user_attempts >= MAX_ATTEMPTS:
        cache.set(keys["user_lockout_key"], lockout_expiry, LOCKOUT_DURATION)
        return True, LOCKOUT_DURATION

    return False, 0


def clear_failed_attempts(request, username=None):
    """
    Clears failed attempt counters and active lockouts upon successful authentication.
    """
    keys = _get_cache_keys(request, username)
    cache.delete(keys["ip_attempts_key"])
    cache.delete(keys["ip_lockout_key"])
    if keys["user_attempts_key"]:
        cache.delete(keys["user_attempts_key"])
    if keys["user_lockout_key"]:
        cache.delete(keys["user_lockout_key"])
