from django.urls import path
from .views import (
    PlayListCreateView,
    PlayDetailView,
    StudentListCreateView,
    StudentDetailView,
    GameListCreateView,
    GameDetailView,
    GameEndAllPlaysView,
    SanctionListCreateView,
    SanctionDetailView,
    ImageListCreateView,
    ImageDetailView,
)

urlpatterns = [
    path("plays/", PlayListCreateView.as_view(), name="plays-list-create"),
    path("plays/<int:pk>/", PlayDetailView.as_view(), name="plays-detail"),
    path("students/", StudentListCreateView.as_view(), name="students-list-create"),
    path("students/<str:pk>/", StudentDetailView.as_view(), name="students-detail"),
    path("games/", GameListCreateView.as_view(), name="games-list-create"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="games-detail"),
    path("games/<int:pk>/end-all-plays/", GameEndAllPlaysView.as_view(), name="games-end-all-plays"),
    path("sanctions/", SanctionListCreateView.as_view(), name="sanctions-list-create"),
    path("sanctions/<int:pk>/", SanctionDetailView.as_view(), name="sanctions-detail"),
    path("images/", ImageListCreateView.as_view(), name="images-list-create"),
    path("images/<int:pk>/", ImageDetailView.as_view(), name="images-detail"),
]
