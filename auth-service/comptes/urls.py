from django.urls import path
from .views import (
    login_view,
    logout_view,
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    ChauffeurLoginAPIView,
    PassagerOnlyAPIView,
    ChauffeurOnlyAPIView,
    UpdateProfileAPIView,
    ChangePasswordAPIView

)

urlpatterns = [
    # Web session login/logout
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Authentication API
    path('api/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('api/me/', MeAPIView.as_view(), name='api-me'),

    # Chauffeur login
    path('api/chauffeur/login/', ChauffeurLoginAPIView.as_view(), name='api-chauffeur-login'),

    # Role-based test endpoints
    path('api/test/passager/', PassagerOnlyAPIView.as_view(), name='test-passager'),
    path('api/test/chauffeur/', ChauffeurOnlyAPIView.as_view(), name='test-chauffeur'),
    path('api/profile/update/', UpdateProfileAPIView.as_view(), name='api-profile-update'),
    path('api/change-password/', ChangePasswordAPIView.as_view(), name='api-change-password'),
]
