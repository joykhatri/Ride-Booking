import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from riders.utils import validate_coordinates ,rider_location


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
#                           Create Ride Module                            #
###########################################################################

class UserRideConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]

        from riders.models import RiderProfile
        try:
            self.user = await sync_to_async(RiderProfile.objects.get)(id=self.user_id)
            if self.user.role == "RIDER":
                await self.close()
            else:
                await self.accept()
        except RiderProfile.DoesNotExist:
            await self.close()

    async def receive(self, text_data):
        from riders.models import Ride
        from asgiref.sync import sync_to_async
        from riders.utils import broadcast_new_ride

        data = json.loads(text_data)
        action = data.get("action")

        if action == "create_ride":
            ride_data = data.get("data")

            ride = await sync_to_async(Ride.objects.create)(
                user = self.user,
                user_name = self.user.name,
                user_phone = self.user.phone,
                pickup_location = ride_data["pickup_location"],
                pickup_latitude = ride_data["pickup_latitude"],
                pickup_longitude = ride_data["pickup_longitude"],
                drop_location = ride_data["drop_location"],
                drop_latitude = ride_data["drop_latitude"],
                drop_longitude = ride_data["drop_longitude"],
                vehicle_type = ride_data["vehicle_type"],
                charges = ride_data["charges"]
            )

            await sync_to_async(broadcast_new_ride)(ride)

            await self.send(text_data=json.dumps({
                "status": True,
                "message": "Ride Created Successfully",
                "data": ride.id
            }))

    async def ride_accepted(self, event):
        await self.send(text_data=json.dumps({
            "status": True,
            "message": "Ride Accepted",
            "data": event["data"]
        }))
            

###########################################################################
#               Nearby Rider can see requested ride Module                #
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

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "accept_ride":
            await self.accept_ride(data.get("ride_id"))
        elif data.get("action") == "decline_ride":
            await self.send(text_data=json.dumps({
                "status": True,
                "message": "Ride declined"
            }))

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
                float(rider.latitude),
                float(rider.longitude),
                float(ride.pickup_latitude),
                float(ride.pickup_longitude)
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

    async def accept_ride(self, ride_id):
        from riders.models import Ride, RiderProfile
        from django.db import transaction

        async with transaction.atomic():
            ride = await sync_to_async(
                Ride.objects.select_for_update().get
            )(id=ride.id)

        if ride.status != "requested":
            await self.send(text_data=json.dumps({
                "status": False,
                "message": "Ride already taken"
            }))
            return
        
        ride.status = "accepted"
        ride.rider_id = self.rider_id
        await sync_to_async(ride.save)()

        await sync_to_async(
            RiderProfile.objects.filter(id=self.rider_id).update
        )(is_available=False)

        await self.channel_layer.group_send(
            f"user_{ride.user_phone}",
            {
                "type": "ride_accepted",
                "data": {
                    "ride_id": ride.id,
                    "rider_id": self.rider_id,
                    "status": "accepted"
                }
            }
        )

        await self.send(text_data=json.dumps({
            "status": True,
            "message": "Ride accepted successfully"
        }))

###########################################################################
#                       Rider Live Location Module                        #
###########################################################################

class RiderLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.rider_id = self.scope['url_route']['kwargs']['rider_id']
        self.group_name = f"rider_location_{self.rider_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from riders.models import RiderProfile

        data = json.loads(text_data)
        lat = data.get('latitude')
        lng = data.get('longitude')

        if validate_coordinates(lat, lng):
            await sync_to_async(RiderProfile.objects.filter(id=self.rider_id).update)(
                latitude = lat,
                longitude = lng
            )

            location_data = rider_location(lat, lng)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'location_update',
                    'data': location_data
                }
            )

    async def location_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
