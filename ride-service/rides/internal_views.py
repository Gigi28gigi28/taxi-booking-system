"""
Internal API endpoints for microservice-to-microservice communication
These endpoints bypass JWT authentication for internal services
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Ride
from .serializers import RideSerializer
from .notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])  # No JWT required for internal calls
def internal_assign_driver(request, ride_id):
    """
    Internal endpoint for matcher worker to assign driver to ride
    
    POST /api/internal/rides/{ride_id}/assign-driver/
    Body: {"driver_id": 105}
    
    This bypasses authentication for internal microservice communication
    """
    logger.info(f" Internal API call: assign driver to ride {ride_id}")
    
    # Get ride
    ride = get_object_or_404(Ride, pk=ride_id)
    
    # Validate ride status
    if ride.status != Ride.STATUS_REQUESTED:
        return Response(
            {
                "detail": "Ride is not in requested state",
                "current_status": ride.status
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get driver_id from request
    driver_id = request.data.get('driver_id')
    if not driver_id:
        return Response(
            {"detail": "driver_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update ride
    ride.driver = driver_id
    ride.status = Ride.STATUS_OFFERED
    ride.save()
    
    logger.info(f" Ride {ride_id} assigned to driver {driver_id}")
    
    # Create notification for driver
    NotificationService.notify_ride_offered(ride)
    
    return Response(
        {
            "success": True,
            "ride": RideSerializer(ride).data,
            "message": f"Driver {driver_id} assigned to ride {ride_id}"
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def internal_get_ride(request, ride_id):
    """
    Internal endpoint to get ride details
    
    GET /api/internal/rides/{ride_id}/
    """
    ride = get_object_or_404(Ride, pk=ride_id)
    return Response(RideSerializer(ride).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def internal_update_status(request, ride_id):
    """
    Internal endpoint to update ride status
    
    POST /api/internal/rides/{ride_id}/update-status/
    Body: {"status": "accepted"}
    """
    ride = get_object_or_404(Ride, pk=ride_id)
    
    new_status = request.data.get('status')
    if not new_status:
        return Response(
            {"detail": "status is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate status
    valid_statuses = [choice[0] for choice in Ride.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response(
            {"detail": f"Invalid status. Must be one of: {valid_statuses}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    ride.status = new_status
    ride.save()
    
    logger.info(f"Ride {ride_id} status updated to {new_status}")
    
    return Response(
        {
            "success": True,
            "ride": RideSerializer(ride).data
        },
        status=status.HTTP_200_OK
    )