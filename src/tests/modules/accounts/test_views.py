import pytest
from rest_framework import status

from tests.factories.user_factory import AdminFactory, UserFactory


TOKEN_URL = "/api/v1/accounts/token/"
REFRESH_URL = "/api/v1/accounts/token/refresh/"


@pytest.mark.django_db
class TestLoginView:
    def test_returns_tokens_for_valid_credentials(self, api_client):
        user = AdminFactory()
        response = api_client.post(TOKEN_URL, {
            "email": user.email,
            "password": "testpass123",
        })

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_returns_tokens_for_non_admin_user(self, api_client):
        """Any user can obtain tokens; authorization is enforced per-endpoint."""
        user = UserFactory(role="rider")
        response = api_client.post(TOKEN_URL, {
            "email": user.email,
            "password": "testpass123",
        })

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_returns_401_for_wrong_password(self, api_client):
        user = AdminFactory()
        response = api_client.post(TOKEN_URL, {
            "email": user.email,
            "password": "wrongpassword",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_401_for_nonexistent_email(self, api_client):
        response = api_client.post(TOKEN_URL, {
            "email": "nobody@example.com",
            "password": "testpass123",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_400_for_missing_email(self, api_client):
        response = api_client.post(TOKEN_URL, {
            "password": "testpass123",
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_for_missing_password(self, api_client):
        AdminFactory(email="test@example.com")
        response = api_client.post(TOKEN_URL, {
            "email": "test@example.com",
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_401_for_inactive_user(self, api_client):
        user = AdminFactory(is_active=False)
        response = api_client.post(TOKEN_URL, {
            "email": user.email,
            "password": "testpass123",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRefreshView:
    def _get_refresh_token(self, api_client, user):
        response = api_client.post(TOKEN_URL, {
            "email": user.email,
            "password": "testpass123",
        })
        return response.data["refresh"]

    def test_returns_new_access_token(self, api_client):
        user = AdminFactory()
        refresh = self._get_refresh_token(api_client, user)

        response = api_client.post(REFRESH_URL, {"refresh": refresh})

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_returns_401_for_invalid_refresh_token(self, api_client):
        response = api_client.post(REFRESH_URL, {"refresh": "invalid-token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_400_for_missing_refresh_token(self, api_client):
        response = api_client.post(REFRESH_URL, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
