import requests
from django.http import JsonResponse
from django.conf import settings

AUTH_VERIFY_URL = settings.AUTH_VERIFY_URL

EXCLUDED_PATHS = [
    "/admin",
    "/admin/",
    "/admin/login/",
    "/admin/logout/",
    "/static",
    "/static/",
    "/favicon.ico",
]

AUTH_PUBLIC_ENDPOINTS = [
    "/accounts/api/login",
    "/accounts/api/register",
    "/accounts/api/verify",
]

def jwt_verification_middleware(get_response):
    """
    Middleware that verifies JWT token with Auth-Service,
    except for admin panel, public routes, and static files.
    """
    def middleware(request):

        path = request.path

        # 1. Skip admin & static
        if any(path.startswith(p) for p in EXCLUDED_PATHS):
            return get_response(request)

        # 2. Skip public auth endpoints
        if any(path.startswith(p) for p in AUTH_PUBLIC_ENDPOINTS):
            return get_response(request)

        # 3. Skip everything that is NOT an API route
        if not path.startswith("/api/"):
            return get_response(request)

        # 4. Extract JWT
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "error": "Missing Authorization Header",
                "detail": "You must provide a Bearer token"
            }, status=401)

        if not auth_header.startswith("Bearer "):
            return JsonResponse({
                "error": "Invalid Authorization format",
                "detail": "Use format: Bearer <token>"
            }, status=401)

        token = auth_header.replace("Bearer ", "").strip()

        # 5. Call Auth-Service to verify
        try:
            response = requests.post(
                AUTH_VERIFY_URL,
                json={"token": token},
                timeout=5
            )
        except requests.exceptions.Timeout:
            return JsonResponse({
                "error": "Auth-Service timeout",
                "detail": "Authentication service is not responding"
            }, status=503)
        except requests.exceptions.ConnectionError:
            return JsonResponse({
                "error": "Auth-Service unreachable",
                "detail": "Cannot connect to authentication service"
            }, status=503)
        except Exception as e:
            return JsonResponse({
                "error": "Auth-Service error",
                "detail": str(e)
            }, status=503)

        # 6. Token invalid
        if response.status_code != 200:
            return JsonResponse({
                "error": "Invalid or expired token",
                "detail": "Your authentication token is not valid"
            }, status=401)

        # 7. Attach user data from auth-service
        user_data = response.json()
        request.user_data = user_data
        request.user_id = user_data.get("id")
        request.user_email = user_data.get("email")
        request.user_role = user_data.get("role")

        return get_response(request)

    return middleware
