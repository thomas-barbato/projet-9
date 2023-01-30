from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("login/", consumers.LoginConsumers.as_asgi()),
]
