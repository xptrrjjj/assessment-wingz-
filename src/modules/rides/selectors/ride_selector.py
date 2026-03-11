from datetime import timedelta

from django.db.models import Prefetch
from django.utils import timezone

from modules.rides.models import Ride, RideEvent


class RideSelector:
    @staticmethod
    def list_rides():
        """
        Return rides with rider, driver, and today's ride events.

        Query budget:
          1) SELECT rides JOIN users (rider) JOIN users (driver) — via select_related
          2) SELECT ride_events WHERE id_ride IN (...) AND created_at >= now-24h — via Prefetch
          3) SELECT COUNT(*) FROM rides — automatic from DRF pagination
        """
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

        todays_events_prefetch = Prefetch(
            "ride_events",
            queryset=RideEvent.objects.filter(
                created_at__gte=twenty_four_hours_ago,
            ).order_by("-created_at"),
            to_attr="todays_ride_events",
        )

        return (
            Ride.objects
            .select_related("id_rider", "id_driver")
            .prefetch_related(todays_events_prefetch)
        )
