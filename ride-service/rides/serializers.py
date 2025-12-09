from rest_framework import serializers
from .models import Ride

class RideSerializer(serializers.ModelSerializer):
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
        read_only_fields = ("id", "status", "driver", "price", "created_at", "updated_at")
