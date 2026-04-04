from django.urls import path

from .consumers import OnlineUsersConsumer, UpdatesConsumer

websocket_urlpatterns = [
    path("ws/users/", OnlineUsersConsumer.as_asgi()),
    path("ws/updates/", UpdatesConsumer.as_asgi()),
]
