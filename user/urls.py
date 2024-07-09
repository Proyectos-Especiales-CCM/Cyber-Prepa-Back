"""
User management URLs.
"""
from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    UserMeDetails,
    UserResetPassword,
    UserResetPasswordConfirm,
)

urlpatterns = [
    # Manage Users
    path("", UserListCreateView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("me/", UserMeDetails.as_view(), name="user-me"),
    path("reset-password/", UserResetPassword.as_view(), name="user-reset-password"),
    path(
        "reset-password-confirm/",
        UserResetPasswordConfirm.as_view(),
        name="user-reset-password-confirm",
    ),
]
