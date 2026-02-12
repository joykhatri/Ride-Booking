import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from riders.utils import validate_coordinates ,rider_location

ride_timeout_tasks = {}

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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from riders.models import RiderProfile, Vehicle
        from riders.utils import distance_km
        from asgiref.sync import sync_to_async

        data = json.loads(text_data)
        user_lat = data.get("latitude")
        user_lng = data.get("longitude")

        if not validate_coordinates(user_lat, user_lng):
            await self.send(text_data=json.dumps({
                "status": False,
                "message": "Invalid Coordinates"
            }))
            return

        riders = await sync_to_async(list)(
            RiderProfile.objects.filter(role="RIDER", is_available=True).select_related('vehicle')
        )

        nearby_riders = []
        for rider in riders:
            if rider.latitude is None or rider.longitude is None:
                continue

            distance = distance_km(
                float(user_lat),
                float(user_lng),
                float(rider.latitude),
                float(rider.longitude),
            )

            if distance <= 5:
                vehicle_type = None
                try:
                    vehicle_type = rider.vehicle.vehicle_type_id
                except Vehicle.DoesNotExist:
                    vehicle_type = "UNKNOWN"
                    
                nearby_riders.append({
                    "latitude": float(rider.latitude),
                    "longitude": float(rider.longitude),
                    "vehicle_type": vehicle_type
                })

        await self.send(text_data=json.dumps({
            "status": True,
            "message": "Available Riders",
            "data": nearby_riders
        }))
    
    async def rider_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


###########################################################################
#                           Create Ride Module                            #
###########################################################################

class UserRideConsumer(AsyncWebsocketConsumer):
    ride_timeout_tasks = {}
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"user_{self.user_id}"

        from riders.models import RiderProfile
        try:
            self.user = await sync_to_async(RiderProfile.objects.get)(id=self.user_id)
            if self.user.role == "RIDER":
                await self.close()
                return
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        except RiderProfile.DoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from riders.models import Ride
        from asgiref.sync import sync_to_async
        from riders.utils import broadcast_new_ride, auto_close_ride
        import asyncio

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
            task = asyncio.create_task(auto_close_ride(self.channel_layer, ride.id, delay_seconds=300))
            ride_timeout_tasks[ride.id] = task

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

    async def ride_declined(self, event):
        await self.send(text_data=json.dumps({
            "status": True,
            "message": "Ride Declined",
            "data": event["data"]
        }))

    async def ride_picked_up(self, event):
        await self.send(text_data=json.dumps({
            "status": True,
            "message": "Ride Picked up",
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
            await self.decline_ride(data.get("ride_id"))
        elif data.get("action") == "picked_up":
            await self.picked_up_ride(
                ride_id = data.get("ride_id"),
                entered_otp = data.get("otp")                     
            )

    async def send_nearby_rides(self):
        from riders.models import Ride, RiderProfile
        from riders.serializers import RideSerializer
        from riders.utils import distance_km
        from asgiref.sync import sync_to_async

        rider = await sync_to_async(RiderProfile.objects.select_related("vehicle").get)(id=self.rider_id)
        rider_vehicle_type = rider.vehicle.vehicle_type_id
        rides = await sync_to_async(list)(
            Ride.objects.filter(status="requested", vehicle_type=rider_vehicle_type)
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
        def accept_ride_db_save():
            from riders.models import Ride, RiderProfile
            from django.db import transaction
            import random

            with transaction.atomic():
                ride = Ride.objects.select_for_update().get(id=ride_id)

                if ride.status != "requested":
                    return None
        
                ride.status = "accepted"
                ride.rider_id = self.rider_id
                otp = str(random.randint(100000, 999999))
                ride.otp = otp
                ride.save()

                rider = RiderProfile.objects.get(id=self.rider_id)
                rider.is_available = False
                rider.save()

                vehicle = rider.vehicle

                return ride, rider, vehicle, otp
            
        result = await sync_to_async(accept_ride_db_save)()
        
        from riders.utils import broadcast_available_riders
        await sync_to_async(broadcast_available_riders)()

        if not result:
            await self.send(text_data=json.dumps({
                "status": False,
                "message": "Ride already taken"
            }))
            return
        
        ride, rider, vehicle, otp = result

        from .consumers import ride_timeout_tasks
        task = ride_timeout_tasks.pop(ride.id, None)
        if task and not task.done():
            task.cancel()
        
        await self.channel_layer.group_send(
            f"user_{ride.user_id}",
            {
                "type": "ride_accepted",
                "data": {
                    "status": "accepted",
                    "ride_id": ride.id,
                    "otp": otp,
                    "rider": {
                        "id": self.rider_id,
                        "name": rider.name,
                        "phone": rider.phone,
                        "vehicle_number": vehicle.vehicle_number
                    }
                }
            }
        )

        await self.send(text_data=json.dumps({
            "status": True,
            "message": "Ride accepted successfully"
        }))

    async def decline_ride(self, ride_id):
        from riders.models import Ride

        ride = await sync_to_async(Ride.objects.get)(id=ride_id)

        if ride.status == "accepted" and ride.rider_id == self.rider_id:
            ride.status = "requested"
            ride.rider_id = None
            ride.otp = None
            await sync_to_async(ride.save)()

            await self.channel_layer.group_send(
                f"user_{ride.user_id}",
                {
                    "type": "ride_declined",
                    "data": {
                        "ride_id": ride.id,
                        "rider_id": self.rider_id,
                        "status": "declined"
                    }
                }
            )
        else:
            await self.send(text_data=json.dumps({
                "status": True,
                "message": "Ride Declined"
            }))

    async def picked_up_ride(self, ride_id, entered_otp):
        from riders.models import Ride
        from asgiref.sync import sync_to_async
        
        ride = await sync_to_async(Ride.objects.get)(id=ride_id)

        if str(ride.otp) != str(entered_otp):
            await self.send(text_data=json.dumps({
                "status": False,
                "message": "Invalid OTP"
            }))
            return

        ride.status = "picked_up"
        await sync_to_async(ride.save)()

        await self.channel_layer.group_send(
            f"user_{ride.user_id}",
            {
                "type": "ride_picked_up",
                "data": {
                    "status": "picked_up",
                    "ride_id": ride_id,
                    }
                }
            )
        
        await self.send(text_data=json.dumps({
            "status": True,
            "message": "Ride Picked up"
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
