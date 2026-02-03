from django.urls import re_path
from .consumers import RiderAvailabilityConsumer, RideConsumer


websocket_urlpatterns = [
    re_path(r"ws/riders/availability/?$", RiderAvailabilityConsumer.as_asgi()),
    re_path(r"ws/riders/new_ride/?$", RideConsumer.as_asgi()),
]