###########################################################################
#                       Rider Avialability Module                         #
###########################################################################

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

###########################################################################
#               Nearby Rider can see requested ride Module                #
###########################################################################

def distance_km(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, asin, sqrt

    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    r = 6371
    return c*r

def broadcast_new_ride(new_ride):
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from riders.models import RiderProfile, Ride
    from riders.serializers import RideSerializer
    from riders.utils import distance_km

    channel_layer = get_channel_layer()

    riders = RiderProfile.objects.filter(is_available=True, role="RIDER")

    for rider in riders:
        if rider.latitude is None or rider.longitude is None:
            continue

        distance = distance_km(
        float(rider.latitude),
        float(rider.longitude),
        float(new_ride.pickup_latitude),
        float(new_ride.pickup_longitude)
        )
        if distance <= 5:
            data = RideSerializer(new_ride).data

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


###########################################################################
#                       Rider Live Location Module                        #
###########################################################################

def validate_coordinates(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        return False
    return -90 <= lat <= 90 and -180 <= lng <= 180

def rider_location(lat, lng):
    return{
        "latitude": float(lat),
        "longitude": float(lng)
    }


###########################################################################
#                       Ride Timeout Module                               #
###########################################################################

async def auto_close_ride(channel_layer, ride_id, delay_seconds=300):
    import asyncio
    from asgiref.sync import sync_to_async
    from riders.models import Ride

    try:
        await asyncio.sleep(delay_seconds)
    except asyncio.CancelledError:
        return

    try:
        ride = await sync_to_async(Ride.objects.get)(id=ride_id)
    except Ride.DoesNotExist:
        return
    
    if ride.status == "requested":
        ride.status = "closed"
        await sync_to_async(ride.save)()

    await channel_layer.group_send(
        f"user_{ride.user_id}",
        {
            "type": "ride_declined",
            "data": {
                "ride_id": ride.id,
                "status": "timeout",
                "message": "No rider accept your ride"
            }
        }
    )