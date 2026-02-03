import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

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