from rest_framework import serializers
from .models import Ride, Notification

class RideSerializer(serializers.ModelSerializer):
    """
    Serializer for Ride model
    
    Important: passenger, driver, status, and price are set by the backend,
    not by user input, so they should be read_only.
    
    Only origin and destination are writable by the user.
    """
    
    class Meta:
        model = Ride
        fields = [
            "id",
            "passenger",
            "driver",
            "origin",
            "destination",
            "status",
            "price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "passenger",      # Set by view based on authenticated user
            "driver",         # Set when ride is offered/accepted
            "status",         # Managed by state transitions
            "price",          # Calculated on completion
            "created_at",
            "updated_at"
        )


class NotificationSerializer(serializers.ModelSerializer):
    ride_details = RideSerializer(source='ride', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'user_id',
            'ride',
            'ride_details',
            'notification_type',
            'title',
            'message',
            'is_read',
            'created_at',
        ]
        read_only_fields = ('id', 'created_at')