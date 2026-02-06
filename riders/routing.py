from django.urls import re_path, path
from .consumers import RiderAvailabilityConsumer, RideConsumer, RiderLocationConsumer


websocket_urlpatterns = [
    re_path(r"ws/riders/availability/?$", RiderAvailabilityConsumer.as_asgi()),
    path(r"ws/riders/new_ride/<int:rider_id>/", RideConsumer.as_asgi()),
    path(r"ws/riders/location/<int:rider_id>/", RiderLocationConsumer.as_asgi()),
]
