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
        self.group_name = "new_rides"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send_rides()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_rides(self):
        from riders.models import Ride
        from riders.serializers import RideSerializer
        from asgiref.sync import sync_to_async

        rides = await sync_to_async(list)(
            Ride.objects.filter(status="requested")
        )
        data = RideSerializer(rides, many=True).data

        await self.send(text_data=json.dumps({
            "event": "send_rides",
            "data": data
        }))

    async def new_ride(self, event):
        await self.send(text_data=json.dumps({
            "event": "new_ride",
            "status": True,
            "message": "New Ride Available",
            "data": event["data"]
        }))

    async def ride_updated(self, event):
        await self.send(text_data=json.dumps({
            "event": "ride_updated",
            "status": True,
            "message": "Ride Updated",
            "data": event["data"]
        }))

    async def ride_deleted(self, event):
        await self.send(text_data=json.dumps({
            "event": "ride_deleted",
            "status": True,
            "message": "Ride Deleted",
            "data": event["data"]
        }))

    async def ride_accepted(self, event):
        await self.send(text_data=json.dumps({
            "event": "ride_accepted",
            "status": True,
            "message": "Ride Accepted",
            "data": event["data"]
        }))

    async def ride_declined(self, event):
        await self.send(text_data=json.dumps({
            "event": "ride_declined",
            "status": True,
            "message": "Ride Declined",
            "data": event["data"]
        }))

    async def ride_completed(self, event):
        await self.send(text_data=json.dumps({
            "event": "ride_completed",
            "status": True,
            "message": "Ride Completed",
            "data": event["data"]
        }))