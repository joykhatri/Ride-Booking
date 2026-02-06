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

def distance_km(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, asin, sqrt

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    r = 6371
    return c*r

def broadcast_new_ride():
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from riders.models import RiderProfile, Ride
    from riders.serializers import RideSerializer

    channel_layer = get_channel_layer()

    riders = RiderProfile.objects.filter(is_available=True, role="RIDER")
    rides = Ride.objects.filter(status="requested")

    for rider in riders:
        if rider.latitude is None or rider.longitude is None:
            continue

        data = RideSerializer(rides, many=True).data

        async_to_sync(channel_layer.group_send)(
            f"rider_{rider.id}",
            {
                "type": "rides_update",
                "data": {
                    "status": True,
                    "message": "Nearby Rides are",
                    "data": data
                }
            }
        )

# For all rides (Show all rides that is in request status and whenever rider accept/decline ride then automatically update)
# def broadcast_new_ride():
#     from asgiref.sync import async_to_sync
#     from channels.layers import get_channel_layer
#     from riders.serializers import RideSerializer
#     from riders.models import Ride

#     channel_layer = get_channel_layer()

#     rides = Ride.objects.filter(status="requested")
#     data = RideSerializer(rides, many=True).data

#     async_to_sync(channel_layer.group_send)(
#         "new_rides",
#         {
#             "type": "rides_update",
#             "data": {
#                 "status": True,
#                 "message": "Available Rides are",
#                 "data": data
#             }
#         }
#     )
