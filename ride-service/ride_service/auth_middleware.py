import requests
from django.http import JsonResponse

AUTH_VERIFY_URL = "http://auth-service:8000/accounts/api/verify/"

def jwt_verification_middleware(get_response):
    def middleware(request):
        # Récupérer le JWT dans le header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({"error": "Missing Authorization Header"}, status=401)

        if not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Invalid Authorization format"}, status=401)

        token = auth_header.replace("Bearer ", "").strip()

        # Appeler AUTH-SERVICE
        try:
            response = requests.post(AUTH_VERIFY_URL, json={"token": token})
        except Exception:
            return JsonResponse({"error": "Auth-Service unreachable"}, status=503)

        if response.status_code != 200:
            return JsonResponse({"error": "Invalid or expired token"}, status=401)

        # Ajouter les données utilisateur à la requête
        request.user_data = response.json()

        return get_response(request)

    return middleware
