from django.urls import path
from .views import (
    StudentListCreateView,
    StudentDetailView,
    GameListCreateView,
    GameDetailView,
    GameEndAllPlaysView,
)

urlpatterns = [
    path("students/", StudentListCreateView.as_view(), name="students-list-create"),
    path("students/<str:pk>/", StudentDetailView.as_view(), name="students-detail"),
    path("games/", GameListCreateView.as_view(), name="games-list-create"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="games-detail"),
    path("games/<int:pk>/end_all_plays/", GameEndAllPlaysView.as_view(), name="games-end-all-plays"),
]
