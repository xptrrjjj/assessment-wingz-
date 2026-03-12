from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from tests.factories.ride_factory import RideEventFactory, RideFactory
from tests.factories.user_factory import DriverFactory, UserFactory


RIDES_URL = "/api/v1/rides/"


@pytest.mark.django_db
class TestRideListViewAuth:
    def test_returns_401_for_unauthenticated_request(self, api_client):
        response = api_client.get(RIDES_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_403_for_non_admin_user(self, rider_client):
        response = rider_client.get(RIDES_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_200_for_admin_user(self, admin_client):
        response = admin_client.get(RIDES_URL)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRideListViewQueryCount:
    def test_list_rides_uses_three_queries_with_pagination(self, admin_client):
        rider = UserFactory()
        driver = DriverFactory()
        rides = RideFactory.create_batch(5, id_rider=rider, id_driver=driver)
        for ride in rides:
            RideEventFactory(id_ride=ride, created_at=timezone.now())

        # 3 queries: COUNT for pagination + rides JOIN users + prefetch events
        with _count_queries() as queries:
            response = admin_client.get(RIDES_URL)

        assert response.status_code == status.HTTP_200_OK
        assert len(queries) == 3, (
            f"Expected 3 queries, got {len(queries)}.\n"
            + "\n".join(f"  [{i+1}] {q['sql']}" for i, q in enumerate(queries))
        )

    def test_query_count_stable_with_many_rides(self, admin_client):
        rider = UserFactory()
        driver = DriverFactory()
        rides = RideFactory.create_batch(25, id_rider=rider, id_driver=driver)
        for ride in rides:
            RideEventFactory(id_ride=ride, created_at=timezone.now())

        with _count_queries() as queries:
            admin_client.get(RIDES_URL)

        assert len(queries) == 3


@pytest.mark.django_db
class TestRideListViewFiltering:
    def test_filter_by_status(self, admin_client):
        rider = UserFactory()
        driver = DriverFactory()
        RideFactory(id_rider=rider, id_driver=driver, status="en-route")
        RideFactory(id_rider=rider, id_driver=driver, status="pickup")
        RideFactory(id_rider=rider, id_driver=driver, status="dropoff")

        response = admin_client.get(RIDES_URL, {"status": "en-route"})

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["status"] == "en-route"

    def test_filter_by_rider_email_exact(self, admin_client):
        rider_a = UserFactory(email="alice@example.com")
        rider_b = UserFactory(email="bob@example.com")
        driver = DriverFactory()
        RideFactory(id_rider=rider_a, id_driver=driver)
        RideFactory(id_rider=rider_b, id_driver=driver)

        response = admin_client.get(RIDES_URL, {"id_rider__email": "alice@example.com"})

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id_rider"]["email"] == "alice@example.com"

    def test_filter_by_rider_email_icontains(self, admin_client):
        rider = UserFactory(email="testuser@example.com")
        driver = DriverFactory()
        RideFactory(id_rider=rider, id_driver=driver)
        RideFactory(id_driver=driver)  # different rider

        response = admin_client.get(RIDES_URL, {"id_rider__email__icontains": "testuser"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestRideListViewSorting:
    def test_sort_by_pickup_time_ascending(self, admin_client):
        rider = UserFactory()
        driver = DriverFactory()
        now = timezone.now()
        old = RideFactory(id_rider=rider, id_driver=driver, pickup_time=now - timedelta(days=5))
        new = RideFactory(id_rider=rider, id_driver=driver, pickup_time=now)

        response = admin_client.get(RIDES_URL, {"ordering": "pickup_time"})

        results = response.data["results"]
        assert results[0]["id_ride"] == old.id_ride
        assert results[1]["id_ride"] == new.id_ride

    def test_sort_by_pickup_time_descending(self, admin_client):
        rider = UserFactory()
        driver = DriverFactory()
        now = timezone.now()
        old = RideFactory(id_rider=rider, id_driver=driver, pickup_time=now - timedelta(days=5))
        new = RideFactory(id_rider=rider, id_driver=driver, pickup_time=now)

        response = admin_client.get(RIDES_URL, {"ordering": "-pickup_time"})

        results = response.data["results"]
        assert results[0]["id_ride"] == new.id_ride
        assert results[1]["id_ride"] == old.id_ride

    def test_sort_by_distance_with_lat_lng(self, admin_client):
        rider = UserFactory()
        driver = DriverFactory()
        # NYC
        near = RideFactory(
            id_rider=rider, id_driver=driver,
            pickup_latitude=40.7128, pickup_longitude=-74.0060,
        )
        # LA
        far = RideFactory(
            id_rider=rider, id_driver=driver,
            pickup_latitude=34.0522, pickup_longitude=-118.2437,
        )

        response = admin_client.get(RIDES_URL, {
            "lat": "40.7580",
            "lng": "-73.9855",
            "ordering": "distance",
        })

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert results[0]["id_ride"] == near.id_ride
        assert results[1]["id_ride"] == far.id_ride
        assert results[0]["distance"] is not None
        assert results[0]["distance"] < results[1]["distance"]


@pytest.mark.django_db
class TestRideListViewPagination:
    def test_response_includes_pagination_fields(self, admin_client):
        rider = UserFactory()
        driver = DriverFactory()
        RideFactory.create_batch(3, id_rider=rider, id_driver=driver)

        response = admin_client.get(RIDES_URL)

        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data
        assert response.data["count"] == 3

    def test_respects_page_size_param(self, admin_client):
        rider = UserFactory()
        driver = DriverFactory()
        RideFactory.create_batch(5, id_rider=rider, id_driver=driver)

        response = admin_client.get(RIDES_URL, {"page_size": 2})

        assert len(response.data["results"]) == 2
        assert response.data["count"] == 5
        assert response.data["next"] is not None


@pytest.mark.django_db
class TestRideListViewResponseShape:
    def test_response_includes_todays_ride_events(self, admin_client):
        ride = RideFactory()
        now = timezone.now()
        RideEventFactory(id_ride=ride, description="Recent", created_at=now - timedelta(hours=1))
        RideEventFactory(id_ride=ride, description="Old", created_at=now - timedelta(hours=48))

        response = admin_client.get(RIDES_URL)

        results = response.data["results"]
        assert len(results) == 1
        events = results[0]["todays_ride_events"]
        assert len(events) == 1
        assert events[0]["description"] == "Recent"

    def test_response_includes_nested_rider_and_driver(self, admin_client):
        ride = RideFactory()

        response = admin_client.get(RIDES_URL)

        result = response.data["results"][0]
        assert "id_user" in result["id_rider"]
        assert "email" in result["id_rider"]
        assert "first_name" in result["id_rider"]
        assert "id_user" in result["id_driver"]
        assert "email" in result["id_driver"]


@pytest.mark.django_db
class TestRideListViewErrorHandling:
    def test_returns_400_for_non_numeric_lat(self, admin_client):
        response = admin_client.get(RIDES_URL, {"lat": "abc", "lng": "-74.0"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"]["type"] == "ValidationError"
        assert "lat" in response.data["error"]["detail"]

    def test_returns_400_for_non_numeric_lng(self, admin_client):
        response = admin_client.get(RIDES_URL, {"lat": "40.0", "lng": "xyz"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"]["type"] == "ValidationError"

    def test_returns_400_for_lat_out_of_range(self, admin_client):
        response = admin_client.get(RIDES_URL, {"lat": "95.0", "lng": "-74.0"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"]["type"] == "ValidationError"
        assert "lat" in response.data["error"]["detail"]

    def test_returns_400_for_lng_out_of_range(self, admin_client):
        response = admin_client.get(RIDES_URL, {"lat": "40.0", "lng": "200.0"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"]["type"] == "ValidationError"
        assert "lng" in response.data["error"]["detail"]

    def test_returns_404_for_nonexistent_ride_detail(self, admin_client):
        response = admin_client.get(f"{RIDES_URL}99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.data

    def test_error_response_matches_standard_shape(self, admin_client):
        response = admin_client.get(RIDES_URL, {"lat": "abc", "lng": "def"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.data["error"]
        assert "type" in error
        assert "detail" in error
        assert "extra" in error

    def test_401_error_matches_standard_shape(self, api_client):
        response = api_client.get(RIDES_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data
        assert "type" in response.data["error"]
        assert "detail" in response.data["error"]

    def test_403_error_matches_standard_shape(self, rider_client):
        response = rider_client.get(RIDES_URL)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "error" in response.data
        assert "type" in response.data["error"]
        assert "detail" in response.data["error"]


class _count_queries:
    """Context manager that captures DB queries for assertion."""

    def __init__(self):
        self._queries = []

    def __enter__(self):
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        self._ctx = CaptureQueriesContext(connection)
        self._ctx.__enter__()
        return self._queries

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ctx.__exit__(exc_type, exc_val, exc_tb)
        self._queries.extend(self._ctx.captured_queries)
