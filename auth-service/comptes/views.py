from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated

from .decorators import rate_limit_login

from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer,
    UserSerializer, ChauffeurLoginSerializer, UpdateProfileSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer
)

from .permissions import IsChauffeur, IsPassager


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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully logged out."}, status=200)

        return Response(serializer.errors, status=400)


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
