import factory

from modules.accounts.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Sequence(lambda n: f"+1555000{n:04d}")
    role = "rider"
    is_active = True
    is_staff = False
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class AdminFactory(UserFactory):
    email = factory.Sequence(lambda n: f"admin{n}@example.com")
    role = "admin"
    is_staff = True


class DriverFactory(UserFactory):
    email = factory.Sequence(lambda n: f"driver{n}@example.com")
    role = "driver"
