from django.contrib import admin
from .models import Ride

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("id", "passenger", "driver", "status", "price", "created_at")
    list_filter = ("status",)
    search_fields = ("passenger__username", "driver__username", "origin", "destination")