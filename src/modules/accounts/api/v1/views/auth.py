from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)


class LoginView(TokenObtainPairView):
    """POST /api/v1/accounts/token/ — obtain access + refresh tokens."""

    permission_classes = []


class RefreshView(BaseTokenRefreshView):
    """POST /api/v1/accounts/token/refresh/ — refresh an access token."""

    permission_classes = []
