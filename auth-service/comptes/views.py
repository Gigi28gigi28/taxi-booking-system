from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .decorators import rate_limit_login
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer,
    UserSerializer, ChauffeurLoginSerializer, UpdateProfileSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer
)

from .permissions import IsChauffeur, IsPassager
User = get_user_model()

# WEB SESSION LOGIN (only web)
@rate_limit_login
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pw = request.POST.get('password')
        user = authenticate(request, email=email, password=pw)

        if user:
            login(request, user)
            return redirect('home')

        messages.error(request, 'Invalid credentials')

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# REGISTER API
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = CustomTokenObtainPairSerializer.get_token(user)

            data = {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# LOGIN API
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @rate_limit_login
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = CustomTokenObtainPairSerializer.get_token(user)

            data = {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            }
            return Response(data, status=200)

        return Response(serializer.errors, status=400)


# LOGOUT
class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


# ME ENDPOINT
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=200)


# CHAUFFEUR LOGIN
class ChauffeurLoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @rate_limit_login
    def post(self, request):
        serializer = ChauffeurLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = CustomTokenObtainPairSerializer.get_token(user)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        }, status=200)


# ROLE-BASED ENDPOINTS
class PassagerOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsPassager]

    def get(self, request):
        return Response(
            {"detail": "Hello passager!", "email": request.user.email},
            status=200
        )


class ChauffeurOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsChauffeur]

    def get(self, request):
        return Response(
            {"detail": "Hello chauffeur!", "email": request.user.email},
            status=200
        )


# UPDATE PROFILE
class UpdateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=200)

        return Response(serializer.errors, status=400)


# CHANGE PASSWORD
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password updated successfully."}, status=200)

        return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_token(request):

    
    print("=" * 60)
    print("🔍 TOKEN VERIFICATION REQUEST")
    print("=" * 60)
    
    try:
        # Get token from request
        token_str = request.data.get("token")
        
        if not token_str:
            print("❌ No token provided in request")
            return Response({"error": "No token provided"}, status=400)
        
        print(f"Token received: {token_str[:50]}...")
        
        # Decode and verify token using SimpleJWT
        try:
            token = AccessToken(token_str)
            print("✅ Token decoded successfully")
        except InvalidToken as e:
            print(f"❌ Token validation failed: {str(e)}")
            return Response({
                "error": "Invalid token",
                "detail": str(e)
            }, status=401)
        except TokenError as e:
            print(f"❌ Token error: {str(e)}")
            return Response({
                "error": "Token error",
                "detail": str(e)
            }, status=401)
        
        # Extract user info from token claims
        user_id = token.get("sub")      # JWT standard: "sub" = subject = user_id
        role = token.get("role")         # Custom claim
        email = token.get("email")       # Custom claim
        
        print(f"📋 Token claims:")
        print(f"   - user_id (sub): {user_id}")
        print(f"   - role: {role}")
        print(f"   - email: {email}")
        
        if not user_id:
            print("❌ No user_id (sub) in token")
            return Response({
                "error": "Invalid token structure",
                "detail": "Token missing 'sub' claim"
            }, status=401)
        
        # Verify user exists in database
        try:
            user = User.objects.get(id=user_id)
            print(f"✅ User found in database: {user.email}")
        except User.DoesNotExist:
            print(f"❌ User {user_id} not found in database")
            return Response({
                "error": "User not found",
                "detail": f"User with id {user_id} does not exist"
            }, status=404)
        
        # Return user info
        response_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
        
        print(f"✅ Returning user data: {response_data}")
        print("=" * 60)
        
        return Response(response_data, status=200)
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        
        return Response({
            "error": "Token verification failed",
            "detail": str(e)
        }, status=401)