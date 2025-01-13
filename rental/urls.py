from django.urls import path
from .views import (
    PlayListCreateView,
    PlayPaginationMetadataView,
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
    StudentSetForgotIdView,
    StudentRemoveForgotIdView,
    NoticeListCreateView,
    NoticeDetailView,
    MaterialListCreateView,
    MaterialDetailView,
    OwedMaterialListCreateView,
    OwedMaterialDetailView,
    OwedMaterialReturnView,
)

urlpatterns = [
    path("plays/", PlayListCreateView.as_view(), name="plays-list-create"),
    path("plays/pagination/", PlayPaginationMetadataView.as_view(), name="plays-pagination"),
    path("plays/<int:pk>/", PlayDetailView.as_view(), name="plays-detail"),
    path("plays/<int:pk>/forgot-id", StudentSetForgotIdView.as_view(), name="plays-forgotten-id"),
    path("students/", StudentListCreateView.as_view(), name="students-list-create"),
    path("students/<str:pk>/", StudentDetailView.as_view(), name="students-detail"),
    path("students/<str:pk>/returned-id", StudentRemoveForgotIdView.as_view(), name="student-returned-id"),
    path("games/", GameListCreateView.as_view(), name="games-list-create"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="games-detail"),
    path("games/<int:pk>/end-all-plays/", GameEndAllPlaysView.as_view(), name="games-end-all-plays"),
    path("sanctions/", SanctionListCreateView.as_view(), name="sanctions-list-create"),
    path("sanctions/<int:pk>/", SanctionDetailView.as_view(), name="sanctions-detail"),
    path("images/", ImageListCreateView.as_view(), name="images-list-create"),
    path("images/<int:pk>/", ImageDetailView.as_view(), name="images-detail"),
    path("notices/", NoticeListCreateView.as_view(), name="notices-list-create"),
    path("notices/<int:pk>/", NoticeDetailView.as_view(), name="notices-detail"),
    path("materials/", MaterialListCreateView.as_view(), name="materials-list-create"),
    path("materials/<int:pk>/", MaterialDetailView.as_view(), name="materials-detail"),
    path("owed-materials/", OwedMaterialListCreateView.as_view(), name="owed-materials-list-create"),
    path("owed-materials/<int:pk>/", OwedMaterialDetailView.as_view(), name="owed-materials-detail"),
    path("owed-materials/<int:pk>/return/", OwedMaterialReturnView.as_view(), name="owed-materials-return"),
]
