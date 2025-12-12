from django.db import models
from django.conf import settings

class Ride(models.Model):
    STATUS_REQUESTED = "requested"
    STATUS_OFFERED = "offered"
    STATUS_ACCEPTED = "accepted"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_OFFERED, "Offered"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    passenger = models.IntegerField()  # user_id venant de Auth-Service
    driver = models.IntegerField(null=True, blank=True)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride {self.id} – {self.status}"
    

class Notification(models.Model):
    """
    Real-time notification system for passengers and drivers
    """
    NOTIFICATION_TYPES = [
        ('ride_requested', 'Ride Requested'),
        ('ride_offered', 'Ride Offered'),
        ('ride_accepted', 'Ride Accepted'),
        ('ride_rejected', 'Ride Rejected'),
        ('ride_completed', 'Ride Completed'),
        ('ride_cancelled', 'Ride Cancelled'),
    ]

    user_id = models.IntegerField()  # passenger_id or driver_id from auth-service
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['user_id', 'is_read']),
        ]

    def __str__(self):
        return f"Notification for User {self.user_id} - {self.notification_type}"

