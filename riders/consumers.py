import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


###########################################################################
#                       Rider Avialability Module                         #
###########################################################################

class RiderAvailabilityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "rider_availability"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send_available_riders()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_available_riders(self):
        from riders.models import RiderProfile
        riders = await sync_to_async(list)(
            RiderProfile.objects.filter(role="RIDER", is_available=True).values(
                "id", "name"
            )
        )
        response = {
            "status": True,
            "message": "Available Riders are",
            "data": riders
        }
        await self.send(text_data=json.dumps(response))

    async def rider_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


###########################################################################
#                       Create Ride Module                                #
###########################################################################

class RideConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.rider_id = self.scope["url_route"]["kwargs"]["rider_id"]
        self.group_name = f"rider_{self.rider_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send_nearby_rides()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_nearby_rides(self):
        from riders.models import Ride, RiderProfile
        from riders.serializers import RideSerializer
        from riders.utils import distance_km
        from asgiref.sync import sync_to_async

        rider = await sync_to_async(RiderProfile.objects.get)(id=self.rider_id)
        
        rides = await sync_to_async(list)(
            Ride.objects.filter(status="requested")
        )

        nearby_rides = []
        for ride in rides:
            distance = distance_km(
                rider.latitude,
                rider.longitude,
                ride.pickup_latitude,
                ride.pickup_longitude
            )
            if distance <= 5:
                nearby_rides.append(ride)

        data = RideSerializer(nearby_rides, many=True).data

        await self.send(text_data=json.dumps({
            "status": True,
            "message": "Nearby Rides",
            "data": data
        }))

    async def rides_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


# For all rides (Show all rides that is in request status and whenever rider accept/decline ride then automatically update)
# class RideConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.group_name = "new_rides"

#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
#         await self.accept()
#         await self.send_rides()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def send_rides(self):
#         from riders.models import Ride
#         from riders.serializers import RideSerializer

#         rides = await sync_to_async(list)(
#             Ride.objects.filter(status="requested")
#         )

#         data = RideSerializer(rides, many=True).data

#         await self.send(text_data=json.dumps({
#             "status": True,
#             "message": "Available rides",
#             "data": data
#         }))

#     async def rides_update(self, event):
#         await self.send(text_data=json.dumps(event["data"]))