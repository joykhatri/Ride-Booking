def broadcast_available_riders():
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from riders.models import RiderProfile
    channel_layer = get_channel_layer()

    riders = list(
        RiderProfile.objects.filter(role="RIDER", is_available=True).values(
            "id", "name"
        )
    )

    async_to_sync(channel_layer.group_send)(
        "rider_availability",
        {
            "type": "rider_update",
            "status": True,
            "message": "Updated Riders are",
            "data": {
                "available_riders": riders
            }
        }
    )


def broadcast_new_ride(event_type, ride):
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from riders.serializers import RideSerializer

    channel_layer = get_channel_layer()

    if isinstance(ride, dict):
        serialized_ride = ride
    else:
        serialized_ride = RideSerializer(ride).data

    async_to_sync(channel_layer.group_send)(
        "new_rides",
        {
            "type": event_type,
            "data": serialized_ride
        }
    )