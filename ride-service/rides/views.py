from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Ride
from .serializers import RideSerializer
from .rabbitmq import publish_message

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def get_queryset(self):
        user = self.request.user_data

        if user["role"] == "ADMIN":
            return Ride.objects.all()

        return Ride.objects.filter(
            passenger_id=user["id"]
        ) | Ride.objects.filter(
            driver_id=user["id"]
        )

    def perform_create(self, serializer):
        user = self.request.user_data

        if user["role"] != "PASSAGER":
            raise PermissionError("Only passengers can request a ride")

        ride = serializer.save(passenger_id=user["id"])

        publish_message("ride.requested", {
            "ride_id": ride.id,
            "origin": ride.origin,
            "destination": ride.destination,
            "passenger_id": user["id"]
        })

        return ride

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        user = request.user_data

        if user["role"] != "CHAUFFEUR":
            return Response({"detail": "Only chauffeurs can accept rides"}, status=403)

        ride = get_object_or_404(Ride, pk=pk)

        if ride.status not in ["requested", "offered"]:
            return Response({"detail": "Ride not available"}, status=400)

        ride.driver_id = user["id"]
        ride.status = "accepted"
        ride.save()

        publish_message("ride.accepted", {
            "ride_id": ride.id,
            "driver_id": user["id"]
        })

        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        user = request.user_data

        if user["role"] != "CHAUFFEUR":
            return Response({"detail": "Only chauffeurs can complete rides"}, status=403)

        ride = get_object_or_404(Ride, pk=pk)

        if ride.status != "accepted":
            return Response({"detail": "Ride not accepted yet"}, status=400)

        ride.price = 10.00
        ride.status = "completed"
        ride.save()

        publish_message("ride.completed", {
            "ride_id": ride.id,
            "price": float(ride.price)
        })

        return Response(RideSerializer(ride).data)
