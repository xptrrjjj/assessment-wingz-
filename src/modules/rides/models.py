from django.conf import settings
from django.db import models


class RideStatus(models.TextChoices):
    EN_ROUTE = "en-route", "En Route"
    PICKUP = "pickup", "Pickup"
    DROPOFF = "dropoff", "Dropoff"


class Ride(models.Model):
    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=RideStatus.choices)
    id_rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rides_as_rider",
        db_column="id_rider",
    )
    id_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rides_as_driver",
        db_column="id_driver",
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "rides"
        verbose_name = "ride"
        verbose_name_plural = "rides"
        ordering = ["-pickup_time"]
        indexes = [
            models.Index(fields=["status"], name="idx_ride_status"),
            models.Index(fields=["pickup_latitude", "pickup_longitude"], name="idx_ride_pickup_coords"),
        ]

    def __str__(self):
        return f"Ride {self.id_ride} ({self.status})"


class RideEvent(models.Model):
    id_ride_event = models.AutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="ride_events",
        db_column="id_ride",
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "ride_events"
        verbose_name = "ride event"
        verbose_name_plural = "ride events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["id_ride", "created_at"], name="idx_ride_event_ride_created"),
        ]

    def __str__(self):
        return f"RideEvent {self.id_ride_event}: {self.description[:50]}"
