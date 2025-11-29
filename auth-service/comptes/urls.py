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
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('api/me/', MeAPIView.as_view(), name='api-me'),
    path('api/chauffeur/login/', ChauffeurLoginAPIView.as_view(), name='api-chauffeur-login'),
    path('api/test/passager/', PassagerOnlyAPIView.as_view(), name='test-passager'),
    path('api/test/chauffeur/', ChauffeurOnlyAPIView.as_view(), name='test-chauffeur'),
    path('api/profile/update/', UpdateProfileAPIView.as_view(), name='api-profile-update'),
    path('api/change-password/', ChangePasswordAPIView.as_view(), name='api-change-password'),
]
