from django.urls import re_path
from .consumers import RiderAvailabilityConsumer

# websocket_urlpatterns = [
#     path("ws/riders/availability/", RiderAvailabilityConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    re_path(r"ws/riders/availability/?$", RiderAvailabilityConsumer.as_asgi()),
]