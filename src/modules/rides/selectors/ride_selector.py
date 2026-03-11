import math
from datetime import timedelta

from django.db.models import F, FloatField, Prefetch, Value
from django.db.models.functions import ACos, Cos, Radians, Sin
from django.utils import timezone

from modules.rides.models import Ride, RideEvent

# Mean Earth radius in kilometres
_EARTH_RADIUS_KM = 6371.0


class RideSelector:
    @staticmethod
    def _todays_events_prefetch():
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        return Prefetch(
            "ride_events",
            queryset=RideEvent.objects.filter(
                created_at__gte=twenty_four_hours_ago,
            ).order_by("-created_at"),
            to_attr="todays_ride_events",
        )

    @staticmethod
    def _base_queryset():
        """Base queryset with select_related and today's events prefetch."""
        return (
            Ride.objects
            .select_related("id_rider", "id_driver")
            .prefetch_related(RideSelector._todays_events_prefetch())
        )

    @staticmethod
    def list_rides():
        """
        Return rides with rider, driver, and today's ride events.

        Query budget:
          1) SELECT rides JOIN users (rider) JOIN users (driver)
          2) SELECT ride_events WHERE id_ride IN (...) AND created_at >= now-24h
          3) SELECT COUNT(*) FROM rides (pagination)
        """
        return RideSelector._base_queryset()

    @staticmethod
    def list_rides_by_distance(*, lat, lng):
        """
        Return rides annotated with distance (km) from the given GPS point
        to each ride's pickup location, using the Haversine formula.

        The annotation is computed in SQL so ORDER BY + LIMIT/OFFSET works
        correctly with pagination — no in-memory sorting.
        """
        lat_rad = math.radians(lat)
        lng_rad = math.radians(lng)

        distance_expr = (
            Value(_EARTH_RADIUS_KM, output_field=FloatField())
            * ACos(
                Cos(Value(lat_rad, output_field=FloatField()))
                * Cos(Radians(F("pickup_latitude")))
                * Cos(Radians(F("pickup_longitude")) - Value(lng_rad, output_field=FloatField()))
                + Sin(Value(lat_rad, output_field=FloatField()))
                * Sin(Radians(F("pickup_latitude")))
            )
        )

        return (
            RideSelector._base_queryset()
            .annotate(distance=distance_expr)
            .order_by("distance")
        )
