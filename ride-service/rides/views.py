import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404

from .models import Ride , Notification
from .serializers import RideSerializer, NotificationSerializer
from .rabbitmq import publish_message
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .notification_service import NotificationService
import logging
from .rabbitmq import (
    publish_ride_requested,
    publish_ride_accepted,
    publish_ride_completed,
    publish_ride_cancelled
)

AUTH_VERIFY_URL = settings.AUTH_VERIFY_URL
def get_user_from_token(request):

    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    if not token:
        return None

    try:
        res = requests.post(AUTH_VERIFY_URL, json={"token": token}, timeout=3)
        if res.status_code != 200:
            return None
        return res.json()   # {id, email, role}
    except:
        return None

logger = logging.getLogger(__name__)


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def get_queryset(self):
        """Filter rides based on authenticated user"""
        user_id = getattr(self.request, 'user_id', None)
        user_role = getattr(self.request, 'user_role', None)
        
        if not user_id:
            return Ride.objects.none()

        if user_role in ["passager", "passenger"]:
            return Ride.objects.filter(passenger=user_id)
        elif user_role in ["chauffeur", "driver"]:
            return Ride.objects.filter(driver=user_id)
        
        return Ride.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Create a new ride (passenger only)
        🔥 NOW WITH RABBITMQ INTEGRATION
        """
        logger.info("\n" + "="*60)
        logger.info("📝 CREATE RIDE REQUEST")
        logger.info("="*60)
        
        # Get authenticated user info
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        logger.info(f"User ID: {user_id}, Role: {user_role}")
        
        if not user_id:
            return Response(
                {"detail": "User ID not found. Authentication failed."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if user_role not in ["passager", "passenger"]:
            return Response(
                {"detail": "Only passengers can request rides"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate input
        origin = request.data.get('origin')
        destination = request.data.get('destination')
        
        if not origin or not destination:
            return Response(
                {"detail": "Both origin and destination are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 1. Create ride in database
            ride = Ride.objects.create(
                passenger=user_id,
                origin=origin,
                destination=destination,
                status=Ride.STATUS_REQUESTED
            )
            
            logger.info(f" Ride created: ID={ride.id}")
            
            # 2. Create notification for passenger
            notification = NotificationService.notify_ride_requested(ride)
            logger.info(f"Notification created: ID={notification.id}")
            
            # 3.  PUBLISH TO RABBITMQ - Matcher Worker will process this
            publish_success = publish_ride_requested(
                ride_id=ride.id,
                passenger_id=user_id,
                origin=origin,
                destination=destination
            )
            
            if publish_success:
                logger.info(f" Published ride.requested to RabbitMQ")
            else:
                logger.warning(f"Failed to publish to RabbitMQ (ride still created)")
            
            return Response(
                RideSerializer(ride).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f" Error creating ride: {str(e)}")
            return Response(
                {"detail": "Error creating ride", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="offer")
    def offer_to_driver(self, request, pk=None):
        """
        Manually offer ride to specific driver (for testing)
        Body: {"driver_id": 123}
        """
        ride = get_object_or_404(Ride, pk=pk)
        
        if ride.status != Ride.STATUS_REQUESTED:
            return Response(
                {"detail": "Ride not available for offer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
        
        # Notify driver
        NotificationService.notify_ride_offered(ride)
        
        logger.info(f" Ride {ride.id} offered to driver {driver_id}")
        
        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """
        Driver accepts the ride offer
         NOW WITH RABBITMQ INTEGRATION
        """
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if user_role not in ["chauffeur", "driver"]:
            return Response(
                {"detail": "Only drivers can accept rides"},
                status=status.HTTP_403_FORBIDDEN
            )

        ride = get_object_or_404(Ride, pk=pk)

        if ride.status != Ride.STATUS_OFFERED:
            return Response(
                {"detail": "Ride is not in offered state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if ride.driver != user_id:
            return Response(
                {"detail": "This ride was not offered to you"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update ride
        ride.status = Ride.STATUS_ACCEPTED
        ride.save()

        # Notify passenger
        NotificationService.notify_ride_accepted(ride)
        
        #  PUBLISH TO RABBITMQ
        publish_ride_accepted(
            ride_id=ride.id,
            driver_id=user_id,
            passenger_id=ride.passenger
        )
        
        logger.info(f" Ride {ride.id} accepted by driver {user_id}")

        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Driver rejects the ride offer"""
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if user_role not in ["chauffeur", "driver"]:
            return Response(
                {"detail": "Only drivers can reject rides"},
                status=status.HTTP_403_FORBIDDEN
            )

        ride = get_object_or_404(Ride, pk=pk)

        if ride.status != Ride.STATUS_OFFERED:
            return Response(
                {"detail": "Ride is not in offered state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if ride.driver != user_id:
            return Response(
                {"detail": "This ride was not offered to you"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Reset to requested (for re-matching)
        ride.driver = None
        ride.status = Ride.STATUS_REQUESTED
        ride.save()

        # Notify passenger
        NotificationService.notify_ride_rejected(ride)
        
        #  RE-PUBLISH to matcher for new driver
        publish_ride_requested(
            ride_id=ride.id,
            passenger_id=ride.passenger,
            origin=ride.origin,
            destination=ride.destination
        )
        
        logger.info(f" Ride {ride.id} rejected, re-queued for matching")

        return Response(
            {"detail": "Ride rejected, searching for another driver"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """
        Complete the ride
         NOW WITH RABBITMQ INTEGRATION
        """
        user_id = getattr(request, 'user_id', None)
        ride = get_object_or_404(Ride, pk=pk)

        if ride.status != Ride.STATUS_ACCEPTED:
            return Response(
                {"detail": "Ride must be accepted before completion"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user_id not in [ride.passenger, ride.driver]:
            return Response(
                {"detail": "Not authorized to complete this ride"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Calculate price
        ride.price = 10.00  # TODO: Dynamic pricing
        ride.status = Ride.STATUS_COMPLETED
        ride.save()

        # Notify both parties
        NotificationService.notify_ride_completed(ride)
        
        #  PUBLISH TO RABBITMQ
        publish_ride_completed(
            ride_id=ride.id,
            driver_id=ride.driver,
            passenger_id=ride.passenger,
            price=float(ride.price)
        )
        
        logger.info(f" Ride {ride.id} completed, price: ${ride.price}")

        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel the ride
         NOW WITH RABBITMQ INTEGRATION
        """
        user_id = getattr(request, 'user_id', None)
        ride = get_object_or_404(Ride, pk=pk)

        if user_id not in [ride.passenger, ride.driver]:
            return Response(
                {"detail": "Not authorized to cancel this ride"},
                status=status.HTTP_403_FORBIDDEN
            )

        ride.status = Ride.STATUS_CANCELLED
        ride.save()

        # Notify the other party
        NotificationService.notify_ride_cancelled(ride, user_id)
        
        #  PUBLISH TO RABBITMQ
        reason = request.data.get('reason', 'User cancelled')
        publish_ride_cancelled(
            ride_id=ride.id,
            cancelled_by=user_id,
            reason=reason
        )
        
        logger.info(f" Ride {ride.id} cancelled by user {user_id}")

        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["get"], url_path="status")
    def get_status(self, request, pk=None):
        """Get real-time ride status for polling"""
        ride = get_object_or_404(Ride, pk=pk)
        
        user_id = getattr(request, 'user_id', None)
        if user_id not in [ride.passenger, ride.driver]:
            return Response(
                {"detail": "Not authorized to view this ride"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get recent notifications (last 5 minutes)
        recent_time = timezone.now() - timedelta(minutes=5)
        recent_notifications = Notification.objects.filter(
            ride=ride,
            user_id=user_id,
            created_at__gte=recent_time
        )
        
        return Response({
            "ride": RideSerializer(ride).data,
            "recent_notifications": NotificationSerializer(recent_notifications, many=True).data
        })