from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # JWT token endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Public API routes (requires JWT)
    path("api/", include("rides.urls")),
    
    # Internal API routes (NO JWT required - for microservices)
    path("api/internal/", include("rides.internal_urls")),
]