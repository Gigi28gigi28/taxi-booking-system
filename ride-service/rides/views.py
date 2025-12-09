import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404

from .models import Ride
from .serializers import RideSerializer
from .rabbitmq import publish_message
from django.conf import settings


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


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def get_queryset(self):
        user = get_user_from_token(self.request)
        if not user:
            return Ride.objects.none()

        if user["role"] == "ADMIN":
            return Ride.objects.all()

        return Ride.objects.filter(passenger=user["id"]) | Ride.objects.filter(driver=user["id"])

    def create(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        if not user or user["role"] != "PASSAGER":
            return Response({"detail": "Permission denied"}, status=403)

        serializer = RideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ride = serializer.save(passenger=user["id"])

        publish_message("ride.requested", {
            "ride_id": ride.id,
            "origin": ride.origin,
            "destination": ride.destination,
            "passenger_id": ride.passenger
        })

        return Response(RideSerializer(ride).data, status=201)

    # DRIVER ACCEPT RIDE
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        user = get_user_from_token(request)
        if not user or user["role"] != "CHAUFFEUR":
            return Response({"detail": "Permission denied"}, status=403)

        ride = get_object_or_404(Ride, pk=pk)

        if ride.status != Ride.STATUS_OFFERED:
            return Response({"detail": "Ride not offered"}, status=400)

        ride.status = Ride.STATUS_ACCEPTED
        ride.driver = user["id"]
        ride.save()

        publish_message("ride.accepted", {
            "ride_id": ride.id,
            "driver_id": user["id"]
        })

        return Response(RideSerializer(ride).data)

    # COMPLETE
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        ride = get_object_or_404(Ride, pk=pk)

        if ride.status != Ride.STATUS_ACCEPTED:
            return Response({"detail": "Ride not accepted"}, status=400)

        ride.price = 10.00
        ride.status = Ride.STATUS_COMPLETED
        ride.save()

        publish_message("ride.completed", {
            "ride_id": ride.id,
            "price": float(ride.price)
        })

        return Response(RideSerializer(ride).data)
