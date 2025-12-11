import requests
from django.http import JsonResponse
from django.conf import settings

AUTH_VERIFY_URL = settings.AUTH_VERIFY_URL

def jwt_verification_middleware(get_response):
    """
    Middleware that verifies JWT token with Auth-Service
    and attaches user data to request.user_data
    """
    
    def middleware(request):
        # Skip auth for admin panel and other non-API routes
        if request.path.startswith('/admin/'):
            return get_response(request)
        
        # Get JWT from Authorization header
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

        # Extract token
        token = auth_header.replace("Bearer ", "").strip()

        # Call Auth-Service to verify token
        try:
            response = requests.post(
                AUTH_VERIFY_URL, 
                json={"token": token},
                timeout=5  # 5 seconds timeout
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

        # Check if token is valid
        if response.status_code != 200:
            return JsonResponse({
                "error": "Invalid or expired token",
                "detail": "Your authentication token is not valid"
            }, status=401)

        # Attach user data to request
        # Auth-Service returns: {id, email, role}
        user_data = response.json()
        request.user_data = user_data
        
        # For convenience, also set individual attributes
        request.user_id = user_data.get("id")
        request.user_email = user_data.get("email")
        request.user_role = user_data.get("role")

        # Continue to the view
        return get_response(request)

    return middleware