from django.urls import path

from modules.accounts.api.v1.views.auth import LoginView, RefreshView

app_name = "accounts"

urlpatterns = [
    path("token/", LoginView.as_view(), name="token-obtain"),
    path("token/refresh/", RefreshView.as_view(), name="token-refresh"),
]
