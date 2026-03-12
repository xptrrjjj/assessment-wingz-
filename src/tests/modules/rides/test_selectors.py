from datetime import timedelta

import pytest
from django.test.utils import override_settings
from django.utils import timezone

from modules.rides.selectors.ride_selector import RideSelector
from tests.factories.ride_factory import RideEventFactory, RideFactory
from tests.factories.user_factory import DriverFactory, UserFactory


@pytest.mark.django_db
class TestRideSelectorListRides:
    def test_returns_rides_with_rider_and_driver_in_two_queries(self):
        """list_rides() must hit the DB with exactly 2 queries (data only)."""
        rider = UserFactory()
        driver = DriverFactory()
        RideFactory.create_batch(5, id_rider=rider, id_driver=driver)

        qs = RideSelector.list_rides()

        # Force evaluation: 1 for rides+users JOIN, 1 for prefetch ride_events
        with pytest.raises(AssertionError) if False else _assert_num_queries(2):
            list(qs)

    def test_todays_ride_events_only_includes_last_24_hours(self):
        ride = RideFactory()
        now = timezone.now()

        recent_event = RideEventFactory(
            id_ride=ride,
            description="Recent event",
            created_at=now - timedelta(hours=1),
        )
        old_event = RideEventFactory(
            id_ride=ride,
            description="Old event",
            created_at=now - timedelta(hours=48),
        )

        qs = RideSelector.list_rides()
        result = list(qs)
        ride_result = result[0]

        assert len(ride_result.todays_ride_events) == 1
        assert ride_result.todays_ride_events[0].id_ride_event == recent_event.id_ride_event

    def test_todays_ride_events_empty_when_no_recent_events(self):
        ride = RideFactory()
        RideEventFactory(
            id_ride=ride,
            created_at=timezone.now() - timedelta(hours=48),
        )

        qs = RideSelector.list_rides()
        result = list(qs)

        assert result[0].todays_ride_events == []

    def test_no_n_plus_one_queries_with_many_rides(self):
        """Query count must stay at 2 regardless of ride count."""
        rider = UserFactory()
        driver = DriverFactory()
        rides = RideFactory.create_batch(20, id_rider=rider, id_driver=driver)
        for ride in rides:
            RideEventFactory(id_ride=ride, created_at=timezone.now())

        qs = RideSelector.list_rides()

        with _assert_num_queries(2):
            results = list(qs)
            # Access nested relations to prove no extra queries fire
            for r in results:
                _ = r.id_rider.email
                _ = r.id_driver.email
                _ = r.todays_ride_events


@pytest.mark.django_db
class TestRideSelectorListRidesByDistance:
    def test_returns_rides_ordered_by_distance(self):
        rider = UserFactory()
        driver = DriverFactory()

        # NYC area
        near_ride = RideFactory(
            id_rider=rider, id_driver=driver,
            pickup_latitude=40.7128, pickup_longitude=-74.0060,
        )
        # LA area
        far_ride = RideFactory(
            id_rider=rider, id_driver=driver,
            pickup_latitude=34.0522, pickup_longitude=-118.2437,
        )

        qs = RideSelector.list_rides_by_distance(lat=40.7580, lng=-73.9855)
        results = list(qs)

        assert results[0].id_ride == near_ride.id_ride
        assert results[1].id_ride == far_ride.id_ride

    def test_annotates_distance_field_on_results(self):
        RideFactory(pickup_latitude=40.7128, pickup_longitude=-74.0060)

        qs = RideSelector.list_rides_by_distance(lat=40.7580, lng=-73.9855)
        result = list(qs)[0]

        assert hasattr(result, "distance")
        assert result.distance is not None
        assert result.distance >= 0

    def test_distance_query_count_is_two(self):
        rider = UserFactory()
        driver = DriverFactory()
        RideFactory.create_batch(10, id_rider=rider, id_driver=driver)

        qs = RideSelector.list_rides_by_distance(lat=40.0, lng=-74.0)

        with _assert_num_queries(2):
            list(qs)


class _assert_num_queries:
    """Context manager that asserts an exact number of DB queries."""

    def __init__(self, expected):
        self.expected = expected

    def __enter__(self):
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        self.ctx = CaptureQueriesContext(connection)
        self.ctx.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx.__exit__(exc_type, exc_val, exc_tb)
        actual = len(self.ctx.captured_queries)
        assert actual == self.expected, (
            f"Expected {self.expected} queries, got {actual}.\n"
            + "\n".join(
                f"  [{i+1}] {q['sql']}"
                for i, q in enumerate(self.ctx.captured_queries)
            )
        )
