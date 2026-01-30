from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import RiderProfile
from .serializers import *
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

###########################################################################
#                       Create Profile                                    #
###########################################################################

class RiderProfileViewSet(viewsets.ModelViewSet):
    queryset = RiderProfile.objects.all()
    serializer_class = RiderProfileSerializer
    
    # For create any User, Rider, Admin
    def create(self, request, *args, **kwargs):
        data = request.data
        # Check Email
        email = data.get("email")
        if not email:
            return Response({
            "success": False,
            "message": "Email is required",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

        elif RiderProfile.objects.filter(email=email).exists():
            return Response({
            "success": False,
            "message": "Email already exist.",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

        # Check Phone
        phone = data.get("phone")
        if not phone:
            return Response({
            "success": False,
            "message": "Phone is required",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

        else:
            digits = "".join(filter(str.isdigit, phone))
            if len(digits) < 10:
                return Response({
                    "success": False,
                    "message": "Phone number must be 10 digits",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
            elif RiderProfile.objects.filter(phone=digits).exists():
                return Response({
                    "success": False,
                    "message": "Phone number already exist.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check Role
            role = data.get("role")
            if not role:
                return Response({
                    "status": False,
                    "message": "Role is required",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)
            
            allowed_role = ['USER', 'RIDER', 'ADMIN']
            if role not in allowed_role:
                return Response({
                    "status": False,
                    "message": f"This role {role} is not allowed",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)


        serializer = RiderProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": f"{role.capitalize()} created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        if user.role != "ADMIN":
            return Response({
                "status": False,
                "message": "You do not have permission",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        rider = self.get_queryset()
        serializer = RiderProfileSerializer(rider, many=True)
        return Response({
            "status": True,
            "message": "List of users",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=401)
        
        if user.role != "ADMIN" and int(pk) != user.id:
            return Response({
                "status": False,
                "message": "You are not allowed to access this data.",
                "data": None
            }, status=403)
        
        try:
            rider = RiderProfile.objects.get(pk=pk)
        except RiderProfile.DoesNotExist:
            return Response({
                "status": False,
                "message": f"User with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RiderProfileSerializer(rider)
        return Response({
            "status": True,
            "message": "Your detail is",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=401)
        
        if user.role != "ADMIN" and int(pk) != user.id:
            return Response({
                "status": False,
                "message": "You are not allowed to update this data.",
                "data": None
            }, status=403)
        
        try:
            rider = RiderProfile.objects.get(pk=pk)
        except RiderProfile.DoesNotExist:
            return Response({
                "status": False,
                "message": f"User with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RiderProfileSerializer(rider, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_data = serializer.validated_data
            has_changes = False
            for field, value in updated_data.items():
                if getattr(rider, field) != value:
                    has_changes = True
                    break

            if not has_changes:
                return Response({
                    "status": True,
                    "message": "No changes detected.",
                    "data": RiderProfileSerializer(rider).data
                }, status=status.HTTP_200_OK)

            serializer.save()
            return Response({
                "status": True,
                "message": "User updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

        
    def destroy(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=401)
        
        if user.role != "ADMIN" and int(pk) != user.id:
            return Response({
                "status": False,
                "message": "You are not allowed to delete this data.",
                "data": None
            }, status=403)
        
        try:
            rider = RiderProfile.objects.get(pk=pk)
        except RiderProfile.DoesNotExist:
            return Response({
                "status": False,
                "message": f"User with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        rider.delete()
        return Response({
            "success": True,
            "message": "User deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)
    

###########################################################################
#                               Login                                     #
###########################################################################

class LoginViewSet(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            error_messages = []
            for field, errors in serializer.errors.items():
                for error in errors:
                    text = str(error).lower()
                    if "required" in text:
                        error_messages.append(f"{field.replace('_',' ').title()} is required.")
                    elif "blank" in text:
                        error_messages.append(f"{field.replace('_',' ').title()} cannot be empty.")
                    else:
                        error_messages.append(str(error))

            return Response({
                "status": False,
                "message": " ".join(error_messages),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        try:
            rider = RiderProfile.objects.get(email=email)
        except RiderProfile.DoesNotExist:
            return Response({
                "status": False,
                "message": "User not exists.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(password, rider.password):
            return Response({
                "status": False,
                "message": "Invalid Password",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        refresh = RefreshToken.for_user(rider)

        return Response({
            "status": True,
            "message": "Login Successful",
            "data": {
                "id": rider.id,
                "name": rider.name,
                "email": rider.email,
                "role": rider.role,
                "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }},
        }, status=status.HTTP_200_OK)


###########################################################################
#                       Vehicle Module                                    #
###########################################################################

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def create(self, request):
        data = request.data
        user = request.user
        if not user or not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission to create vehicle.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        vehicle_type = data.get("vehicle_type")
        vehicle_number = data.get("vehicle_number")

        allowed_vehicle_types = ["BIKE", "CAR", "AUTO"]

        # Vehicle number check
        if not vehicle_number:
            return Response({
                "status": False,
                "message": "Vehicle number is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Vehicle type check
        if not vehicle_type:
            return Response({
                "status": False,
                "message": "Vehicle type is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if vehicle_type not in allowed_vehicle_types:
            return Response({
                "status": False,
                "message": f"Invalid vehicle type. Allowed vehicles are {allowed_vehicle_types}.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if Vehicle.objects.filter(rider=user).exists():
            return Response({
                "status": False,
                "message": "Vehicle already exists for this rider",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        vehicle_number = request.data.get("vehicle_number")
        if vehicle_number and Vehicle.objects.filter(vehicle_number=vehicle_number).exists():
            return Response({
                "status": False,
                "message": "This vehicle number is already registered by another rider.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(rider=request.user)
            return Response({
                "status": True,
                "message": "Vehicle created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        if user.role != "ADMIN":
            return Response({
                "status": False,
                "message": "You do not have permission to view vehicle.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)   
        
        vehicle = self.get_queryset()
        serializer = VehicleSerializer(vehicle, many=True)
        return Response({
            "status": True,
            "message": "List of vehicles",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission to view vehicle.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            vehicle = Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Vehicle with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.role == "RIDER" and vehicle.rider != user:
            return Response({
                "status": False,
                "message": "You are not allowed to access this vehicle.",
                "data": None
            }, status=403)

        serializer = VehicleSerializer(vehicle)
        return Response({
            "status": True,
            "message": "Vehicle detail is",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        data = request.data
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission to update vehicle.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        vehicle_type = data.get("vehicle_type")
        vehicle_number = data.get("vehicle_number")

        allowed_vehicle_types = ["BIKE", "CAR", "AUTO"]

        # Vehicle number check
        if not vehicle_number:
            return Response({
                "status": False,
                "message": "Vehicle number is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Vehicle type check
        if not vehicle_type:
            return Response({
                "status": False,
                "message": "Vehicle type is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if vehicle_type not in allowed_vehicle_types:
            return Response({
                "status": False,
                "message": f"Invalid vehicle type. Allowed vehicles are {allowed_vehicle_types}.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            vehicle = Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Vehicle with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        
        if user.role == "RIDER" and vehicle.rider != user:
            return Response({
                "status": False,
                "message": "You are not allowed to update this vehicle.",
                "data": None
            }, status=403)

        vehicle_number = request.data.get("vehicle_number")
        if vehicle_number and Vehicle.objects.exclude(id=vehicle.id).filter(vehicle_number=vehicle_number).exists():
            return Response({
                "status": False,
                "message": "This vehicle number is already registered by another rider.",
                "data": None
            }, status=400)
        
        serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_data = serializer.validated_data
            has_changes = False
            for field, value in updated_data.items():
                if getattr(vehicle, field) != value:
                    has_changes = True
                    break

            if not has_changes:
                return Response({
                    "status": True,
                    "message": "No changes detected.",
                    "data": VehicleSerializer(vehicle).data
                }, status=status.HTTP_200_OK)

            serializer.save()
            return Response({
                "status": True,
                "message": "Vehicle updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission to view vehicle.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            vehicle = Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Vehicle with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.role == "RIDER" and vehicle.rider != user:
            return Response({
                "status": False,
                "message": "You are not allowed to delete this vehicle.",
                "data": None
            }, status=403)

        vehicle.delete()
        return Response({
            "status": True,
            "message": "Vehicle deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)
    

###########################################################################
#                       Ride Module                                       #
###########################################################################
    
class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def create(self, request):
        data = request.data
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role == "RIDER":
            return Response({
                "status": False,
                "message": "Riders are not allowed to book ride.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        charges = data.get("charges")
        if not charges:
            return Response({
                "status": False,
                "message": "Charges is required",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if charges<0:
            return Response({
                "status": False,
                "message": "Charges must be greater than 0",
                "data": None
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        vehicle_type = data.get("vehicle_type")
        allowed_vehicle_types = ["BIKE", "CAR", "AUTO"]

        if not vehicle_type:
            return Response({
                "status": False,
                "message": "Vehicle type is required",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if vehicle_type not in allowed_vehicle_types:
            return Response({
                "status": False,
                "message": f"Invalid vehicle type. Allowed vehicles are {allowed_vehicle_types}.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = RideSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_name=user.name, user_phone=user.phone)
            return Response({
                "status": True,
                "message": "Ride created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    

    def update(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["USER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "Rider do not have permission to update ride.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Ride with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.role == "USER":
            if ride.user_phone != user.phone:
                return Response({
                    "status": False,
                    "message": "You are not allowed to update this ride.",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

        serializer = RideSerializer(ride, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Ride updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    

    def destroy(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["USER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "Rider do not have permission to delete ride.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Ride with id {pk} does not exist",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.role == "USER":
            if ride.user_phone != user.phone:
                return Response({
                    "status": False,
                    "message": "You are not allowed to delete this ride.",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

        ride.delete()
        return Response({
            "status": True,
            "message": "Ride deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)




    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        user = request.user
        ride = Ride.objects.get(pk=pk)
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if rider has a vehicle
        if not Vehicle.objects.filter(rider=user).exists():
            return Response({
                "status": False,
                "message": "You must have a registered vehicle to accept rides.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not Vehicle.objects.filter(rider=user, vehicle_type=ride.vehicle_type).exists():
            return Response({
                "status": False,
                "message": f"You do not have {ride.vehicle_type} to accept this ride.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ride = Ride.objects.get(pk=pk)
        except Ride.DoesNotExist:
            return Response({
                "status": False,
                "message": "Ride not found or not assigned to you",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        if ride.status != 'requested':
            return Response({
                "status": False,
                "message": f"Cannot accept ride with status '{ride.status}'",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        rider_profile = RiderProfile.objects.get(name=user)
        ride.rider = rider_profile
        ride.status = 'accepted'
        ride.save()

        return Response({
            "status": True,
            "message": "Ride accepted",
            "data": RideSerializer(ride).data
        })

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if rider has a vehicle
        if not Vehicle.objects.filter(rider=user).exists():
            return Response({
                "status": False,
                "message": "You must have a registered vehicle to decline rides.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ride = Ride.objects.get(pk=pk, rider=user)
        except Ride.DoesNotExist:
            return Response({
                "status": False,
                "message": "Ride not found or not assigned to you",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        if ride.status != 'requested':
            return Response({
                "status": False,
                "message": f"Cannot decline ride with status '{ride.status}'",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        rider_profile = RiderProfile.objects.get(name=user)
        ride.rider = rider_profile
        ride.status = 'declined'
        ride.save()

        return Response({
            "status": True,
            "message": "Ride declined",
            "data": RideSerializer(ride).data
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if rider has a vehicle
        if not Vehicle.objects.filter(rider=user).exists():
            return Response({
                "status": False,
                "message": "You must have a registered vehicle to complete rides.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ride = Ride.objects.get(pk=pk, rider=user)
        except Ride.DoesNotExist:
            return Response({
                "status": False,
                "message": "Ride not found or not assigned to you",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        if ride.status != 'accepted':
            return Response({
                "status": False,
                "message": f"Cannot complete ride with status '{ride.status}'",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        rider_profile = RiderProfile.objects.get(name=user)
        ride.rider = rider_profile
        ride.status = 'completed'
        ride.save()

        return Response({
            "status": True,
            "message": "Ride completed",
            "data": RideSerializer(ride).data
        })


###########################################################################
#                       Payment Module                                    #
###########################################################################

class RiderPaymentViewSet(viewsets.ModelViewSet):
    queryset = RiderPayment.objects.all()
    serializer_class = RiderPaymentSerializer

    # Create a payment for a ride
    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
        ride = Ride.objects.get(pk=pk)
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            ride = Ride.objects.get(pk=pk, rider=user)
        except Ride.DoesNotExist:
            return Response({
                "status": False,
                "message": "Ride not found",
                "data": None}, status=status.HTTP_404_NOT_FOUND)

        if ride.status != "completed":
            return Response({
                "status": False,
                "message": "You do not create payment before complete the ride",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if RiderPayment.objects.filter(ride=ride).exists():
            return Response({
                "status": False,
                "message": "Payment already created",
                "data": None}, status=status.HTTP_400_BAD_REQUEST)

        payment = RiderPayment.objects.create(
            ride=ride,
            rider=user,
            amount=ride.charges
        )

        return Response({
            "status": True,
            "message": "Payment created",
            "data": RiderPaymentSerializer(payment).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role not in ["RIDER", "ADMIN"]:
            return Response({
                "status": False,
                "message": "You do not have permission",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            ride = Ride.objects.get(pk=pk, rider=user)
            payment = RiderPayment.objects.get(ride=ride)
        except (Ride.DoesNotExist, RiderPayment.DoesNotExist):
            return Response({
                "status": False,
                "message": "Ride or payment not found",
                "data": None}, status=status.HTTP_404_NOT_FOUND)

        payment.paid = True
        payment.save()

        return Response({
            "status": True,
            "message": "Payment paid",
            "data": RiderPaymentSerializer(payment).data
        }, status=status.HTTP_202_ACCEPTED)