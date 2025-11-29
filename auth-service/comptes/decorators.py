from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from functools import wraps
import time


def get_request_object(*args):
    if len(args) == 0:
        return None

    # Class-based view: first arg = self, second = request
    if hasattr(args[0], 'request'):
        return args[0].request

    # Function-based view: first arg = request
    return args[0]


def rate_limit_login(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request = get_request_object(*args)
        if request is None:
            return view_func(*args, **kwargs)

        LIMIT = settings.LOGIN_RATE_LIMIT["MAX_ATTEMPTS"]
        WINDOW = settings.LOGIN_RATE_LIMIT["WINDOW_MINUTES"] * 60
        BLOCK_TIME = settings.LOGIN_RATE_LIMIT["BLOCK_MINUTES"] * 60

        ip = request.META.get("REMOTE_ADDR", "unknown")

        # body might be JSON → use .data
        try:
            email = request.data.get("email", "") if hasattr(request, "data") else ""
        except:
            email = ""

        key = f"login-attempts:{ip}:{email}"
        block_key = f"login-blocked:{ip}:{email}"

        # Check if blocked
        if cache.get(block_key):
            return JsonResponse(
                {"detail": "Too many login attempts. Try again later."},
                status=429
            )

        # Increment attempts
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, WINDOW)

        # If exceeds limit → block
        if attempts > LIMIT:
            cache.set(block_key, True, BLOCK_TIME)
            return JsonResponse(
                {"detail": "Too many login attempts. Try again later."},
                status=429
            )

        return view_func(*args, **kwargs)

    return wrapper
