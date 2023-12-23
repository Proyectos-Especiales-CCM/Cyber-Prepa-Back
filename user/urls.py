from django.urls import path
from .views import UserListCreateView, UserDetailView, UserMeDetails

urlpatterns = [
    # Manage Users
    path("", UserListCreateView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("me/", UserMeDetails.as_view(), name="user-me"),
]
