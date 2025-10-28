# accounts/urls.py
from django.urls import path
from .views import (
    register_user,
    login_user,
    logout_user,
    me,
    token_login,
    upgrade,
    logout_token,
    downgrade,
    status,
)

app_name = "accounts"

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("me/", me, name="me"),
    path("token-login/", token_login, name="token-login"),
    path("upgrade/", upgrade, name="upgrade"),
    path("logout-token/", logout_token, name="logout-token"),
    path("status/", status, name="status"),
    path("downgrade/", downgrade, name="downgrade"),
]
