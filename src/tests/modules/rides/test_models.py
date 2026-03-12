import pytest
from django.db import IntegrityError
from django.utils import timezone

from tests.factories.ride_factory import RideFactory, RideEventFactory
from tests.factories.user_factory import UserFactory, DriverFactory, AdminFactory


@pytest.mark.django_db
class TestUserModel:
    def test_str_returns_email(self):
        user = UserFactory(email="display@example.com")
        assert str(user) == "display@example.com"

    def test_email_must_be_unique(self):
        UserFactory(email="dup@example.com")
        with pytest.raises(IntegrityError):
            UserFactory(email="dup@example.com")

    def test_default_role_is_rider(self):
        user = UserFactory()
        assert user.role == "rider"

    def test_admin_factory_sets_admin_role(self):
        user = AdminFactory()
        assert user.role == "admin"
        assert user.is_staff is True

    def test_driver_factory_sets_driver_role(self):
        user = DriverFactory()
        assert user.role == "driver"

    def test_password_is_hashed(self):
        user = UserFactory()
        assert user.password != "testpass123"
        assert user.check_password("testpass123")


@pytest.mark.django_db
class TestRideModel:
    def test_str_includes_id_and_status(self):
        ride = RideFactory(status="pickup")
        assert f"Ride {ride.id_ride}" in str(ride)
        assert "pickup" in str(ride)

    def test_default_ordering_is_pickup_time_descending(self):
        from modules.rides.models import Ride

        rider = UserFactory()
        driver = DriverFactory()
        now = timezone.now()
        old = RideFactory(
            id_rider=rider, id_driver=driver,
            pickup_time=now - timezone.timedelta(days=5),
        )
        new = RideFactory(
            id_rider=rider, id_driver=driver,
            pickup_time=now,
        )

        rides = list(Ride.objects.all())
        assert rides[0].id_ride == new.id_ride
        assert rides[1].id_ride == old.id_ride

    def test_rider_and_driver_are_required(self):
        with pytest.raises(IntegrityError):
            from modules.rides.models import Ride
            Ride.objects.create(
                status="en-route",
                pickup_latitude=40.0,
                pickup_longitude=-74.0,
                dropoff_latitude=40.1,
                dropoff_longitude=-74.1,
                pickup_time=timezone.now(),
            )

    def test_cascade_deletes_events_when_ride_deleted(self):
        from modules.rides.models import RideEvent

        ride = RideFactory()
        ride_pk = ride.id_ride
        RideEventFactory(id_ride=ride)
        RideEventFactory(id_ride=ride)
        assert RideEvent.objects.filter(id_ride=ride_pk).count() == 2

        ride.delete()
        assert RideEvent.objects.filter(id_ride=ride_pk).count() == 0


@pytest.mark.django_db
class TestRideEventModel:
    def test_str_includes_id_and_description(self):
        event = RideEventFactory(description="Status changed to pickup")
        assert f"RideEvent {event.id_ride_event}" in str(event)
        assert "Status changed to pickup" in str(event)

    def test_str_truncates_long_description(self):
        long_desc = "A" * 100
        event = RideEventFactory(description=long_desc)
        assert str(event) == f"RideEvent {event.id_ride_event}: {'A' * 50}"

    def test_default_ordering_is_created_at_descending(self):
        from modules.rides.models import RideEvent

        ride = RideFactory()
        now = timezone.now()
        old = RideEventFactory(
            id_ride=ride,
            created_at=now - timezone.timedelta(hours=5),
        )
        new = RideEventFactory(
            id_ride=ride,
            created_at=now,
        )

        events = list(RideEvent.objects.filter(id_ride=ride))
        assert events[0].id_ride_event == new.id_ride_event
        assert events[1].id_ride_event == old.id_ride_event
