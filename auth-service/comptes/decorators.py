import time
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from rest_framework.response import Response
from rest_framework import status
MAX_ATTEMPTS = getattr(settings, "LOGIN_RATE_LIMIT", {}).get("MAX_ATTEMPTS", 5)
WINDOW = getattr(settings, "LOGIN_RATE_LIMIT", {}).get("WINDOW_MINUTES", 15) * 60  # seconds
BLOCK_TIME = getattr(settings, "LOGIN_RATE_LIMIT", {}).get("BLOCK_MINUTES", 15) * 60  # seconds


def rate_limit_login(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Get email/username from request
        email = request.POST.get("email") or request.data.get("email")
        ip = get_client_ip(request)
        cache_key = f"login_attempts:{email}:{ip}"

        # Get current attempts
        attempt_data = cache.get(cache_key, {"count": 0, "first_attempt": time.time()})
        elapsed = time.time() - attempt_data["first_attempt"]

        # If blocked
        if attempt_data["count"] >= MAX_ATTEMPTS and elapsed <= BLOCK_TIME:
            message = f"Too many login attempts. Try again in {int((BLOCK_TIME - elapsed) / 60)+1} minutes."
            if hasattr(request, "data"):  # DRF API
                return Response({"detail": message}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:  # Django web
                messages.error(request, message)
                return view_func(request, *args, **kwargs)

        # Call the actual view
        response = view_func(request, *args, **kwargs)

        # Determine if login failed
        failed = False
        if hasattr(response, "status_code"):  # DRF
            if response.status_code in [400, 401]:
                failed = True
        else: 
            from django.contrib.messages import get_messages
            if any(msg.level_tag == "error" for msg in get_messages(request)):
                failed = True

        # Update attempts
        if failed:
            if elapsed > WINDOW:
                # Reset counter after window
                attempt_data = {"count": 1, "first_attempt": time.time()}
            else:
                attempt_data["count"] += 1
        else:
            # Successful login → clear attempts
            attempt_data = {"count": 0, "first_attempt": time.time()}

        cache.set(cache_key, attempt_data, timeout=BLOCK_TIME)
        return response

    return _wrapped_view


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
