from django.contrib import admin
from .models import Ride, Notification

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("id", "passenger", "driver", "status", "price", "created_at")
    list_filter = ("status",)
    search_fields = ("passenger", "driver", "origin", "destination")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("user_id", "title", "message")
    readonly_fields = ("created_at",)