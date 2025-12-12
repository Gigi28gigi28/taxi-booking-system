from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RideViewSet
from .notification_views import NotificationViewSet

router = DefaultRouter()
router.register("rides", RideViewSet, basename="rides")
router.register("notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("", include(router.urls)),
    
]
