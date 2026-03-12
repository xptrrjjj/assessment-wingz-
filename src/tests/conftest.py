import pytest
from rest_framework.test import APIClient

from tests.factories.user_factory import AdminFactory, UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return AdminFactory()


@pytest.fixture
def rider_user(db):
    return UserFactory(role="rider")


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def rider_client(api_client, rider_user):
    api_client.force_authenticate(user=rider_user)
    return api_client
