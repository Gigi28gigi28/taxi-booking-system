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


# ============================================================
# FILE: ride-service/rides/views.py
# FINAL FIXED VERSION
# ============================================================

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .models import Ride, Notification
from .serializers import RideSerializer, NotificationSerializer
from .notification_service import NotificationService


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def get_queryset(self):
        """
        Filter rides based on authenticated user
        """
        user_id = getattr(self.request, 'user_id', None)
        user_role = getattr(self.request, 'user_role', None)
        
        if not user_id:
            return Ride.objects.none()

        # Passengers see their own rides
        if user_role in ["passager", "passenger"]:
            return Ride.objects.filter(passenger=user_id)
        
        # Drivers see rides assigned to them
        elif user_role in ["chauffeur", "driver"]:
            return Ride.objects.filter(driver=user_id)
        
        return Ride.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Create a new ride (passenger only)
        
        🔥 KEY FIX: We validate ONLY origin/destination from user input,
        then add passenger from authenticated user AFTER validation
        """
        print("\n" + "="*60)
        print("📝 CREATE RIDE REQUEST")
        print("="*60)
        
        # Get authenticated user info
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        user_email = getattr(request, 'user_email', None)
        
        print(f"User ID: {user_id}")
        print(f"User Role: {user_role}")
        print(f"User Email: {user_email}")
        print(f"Request data: {request.data}")
        
        # Check if user data exists
        if not user_id:
            return Response(
                {"detail": "User ID not found. Authentication may have failed."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check role (accept both spellings)
        if user_role not in ["passager", "passenger"]:
            return Response(
                {
                    "detail": "Only passengers can request rides",
                    "your_role": user_role
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate input data (only origin and destination from user)
        if not request.data:
            return Response(
                {"detail": "No data provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        origin = request.data.get('origin')
        destination = request.data.get('destination')
        
        if not origin or not destination:
            return Response(
                {
                    "detail": "Both origin and destination are required",
                    "received": {
                        "origin": origin,
                        "destination": destination
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 🔥 Create ride directly (bypass serializer for passenger field)
        try:
            ride = Ride.objects.create(
                passenger=user_id,
                origin=origin,
                destination=destination,
                status=Ride.STATUS_REQUESTED
            )
            
            print(f"✅ Ride created: ID={ride.id}, Status={ride.status}")
            
            # Create notification for passenger
            notification = NotificationService.notify_ride_requested(ride)
            print(f"✅ Notification created: ID={notification.id}")
            
            return Response(
                RideSerializer(ride).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            print(f"❌ Error creating ride: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response(
                {
                    "detail": "Error creating ride",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ========== DRIVER ACTIONS ==========

    @action(detail=True, methods=["post"], url_path="offer")
    def offer_to_driver(self, request, pk=None):
        """
        Manually offer ride to a specific driver (for testing without RabbitMQ)
        Body: {"driver_id": 123}
        """
        ride = get_object_or_404(Ride, pk=pk)
        
        if ride.status != Ride.STATUS_REQUESTED:
            return Response(
                {
                    "detail": "Ride is not available for offer",
                    "current_status": ride.status
                },
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
        
        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """
        Driver accepts the ride offer
        """
        user_id = getattr(request, 'user_id', None)
        user_role = getattr(request, 'user_role', None)
        
        if user_role not in ["chauffeur", "driver"]:
            return Response(
                {
                    "detail": "Only drivers can accept rides",
                    "your_role": user_role
                },
                status=status.HTTP_403_FORBIDDEN
            )

        ride = get_object_or_404(Ride, pk=pk)

        # Validate ride state
        if ride.status != Ride.STATUS_OFFERED:
            return Response(
                {
                    "detail": "Ride is not in offered state",
                    "current_status": ride.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate this driver was offered the ride
        if ride.driver != user_id:
            return Response(
                {
                    "detail": "This ride was not offered to you",
                    "offered_to_driver": ride.driver,
                    "your_id": user_id
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Update ride
        ride.status = Ride.STATUS_ACCEPTED
        ride.save()

        # Notify passenger
        NotificationService.notify_ride_accepted(ride)

        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """
        Driver rejects the ride offer
        """
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
                {
                    "detail": "Ride is not in offered state",
                    "current_status": ride.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if ride.driver != user_id:
            return Response(
                {"detail": "This ride was not offered to you"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Reset ride to requested state (for re-matching)
        ride.driver = None
        ride.status = Ride.STATUS_REQUESTED
        ride.save()

        # Notify passenger
        NotificationService.notify_ride_rejected(ride)

        return Response(
            {"detail": "Ride rejected successfully", "ride": RideSerializer(ride).data},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """
        Complete the ride (driver or passenger can trigger)
        """
        user_id = getattr(request, 'user_id', None)
        ride = get_object_or_404(Ride, pk=pk)

        if ride.status != Ride.STATUS_ACCEPTED:
            return Response(
                {
                    "detail": "Ride must be accepted before completion",
                    "current_status": ride.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only driver or passenger involved can complete
        if user_id not in [ride.passenger, ride.driver]:
            return Response(
                {"detail": "You are not authorized to complete this ride"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Calculate price (you can make this dynamic later)
        ride.price = 10.00
        ride.status = Ride.STATUS_COMPLETED
        ride.save()

        # Notify both parties
        NotificationService.notify_ride_completed(ride)

        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel the ride
        """
        user_id = getattr(request, 'user_id', None)
        ride = get_object_or_404(Ride, pk=pk)

        # Only passenger or assigned driver can cancel
        if user_id not in [ride.passenger, ride.driver]:
            return Response(
                {"detail": "You are not authorized to cancel this ride"},
                status=status.HTTP_403_FORBIDDEN
            )

        ride.status = Ride.STATUS_CANCELLED
        ride.save()

        # Notify the other party
        NotificationService.notify_ride_cancelled(ride, user_id)

        return Response(RideSerializer(ride).data)

    # ========== REAL-TIME STATUS POLLING ==========

    @action(detail=True, methods=["get"], url_path="status")
    def get_status(self, request, pk=None):
        """
        Get real-time ride status updates
        Used for polling by frontend
        """
        ride = get_object_or_404(Ride, pk=pk)
        
        # Check authorization
        user_id = getattr(request, 'user_id', None)
        if user_id not in [ride.passenger, ride.driver]:
            return Response(
                {"detail": "Not authorized to view this ride"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get recent notifications for this ride (last 5 minutes)
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