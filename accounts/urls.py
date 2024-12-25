from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

app_name = "accounts"
urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("resign/", views.resign, name="resign"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("<int:user_pk>/follow/", views.follow, name="follow"),
]

urlpatterns += [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
]

from .views import ChangePasswordView

urlpatterns += [
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]