"""
Internal API routes for microservice-to-microservice communication
"""
from django.urls import path
from .internal_views import (
    internal_assign_driver,
    internal_get_ride,
    internal_update_status
)

urlpatterns = [
    path('rides/<int:ride_id>/assign-driver/', internal_assign_driver, name='internal-assign-driver'),
    path('rides/<int:ride_id>/', internal_get_ride, name='internal-get-ride'),
    path('rides/<int:ride_id>/update-status/', internal_update_status, name='internal-update-status'),
]