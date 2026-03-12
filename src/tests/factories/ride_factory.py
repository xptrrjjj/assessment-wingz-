import factory
from django.utils import timezone

from modules.rides.models import Ride, RideEvent
from tests.factories.user_factory import DriverFactory, UserFactory


class RideFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ride

    status = "en-route"
    id_rider = factory.SubFactory(UserFactory)
    id_driver = factory.SubFactory(DriverFactory)
    pickup_latitude = factory.Faker("latitude")
    pickup_longitude = factory.Faker("longitude")
    dropoff_latitude = factory.Faker("latitude")
    dropoff_longitude = factory.Faker("longitude")
    pickup_time = factory.LazyFunction(timezone.now)


class RideEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RideEvent

    id_ride = factory.SubFactory(RideFactory)
    description = "Status changed to pickup"
    created_at = factory.LazyFunction(timezone.now)
