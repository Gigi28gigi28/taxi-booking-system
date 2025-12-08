from django.db import models

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

    passenger_id = models.IntegerField()     # venant du Auth-Service
    driver_id = models.IntegerField(null=True, blank=True)

    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ride {self.id} ({self.status})"
