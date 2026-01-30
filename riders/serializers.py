from rest_framework import serializers
from .models import RiderProfile, Vehicle, Ride, RiderPayment
from django.contrib.auth.hashers import make_password

class RiderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderProfile
        fields = ['id', 'name', 'email', 'phone', 'password', 'role', 'created_at']
        extra_kwargs = {'password' : {'write_only': True}}

    # def validate_phone(self, value):
    #     digits = ''.join(filter(str.isdigit, value))
    #     if len(digits) < 10:
    #         raise serializers.ValidationError("Phone number must be at least 10 digits")

    #     rider_id = self.instance.id if self.instance else None
    #     if RiderProfile.objects.exclude(id=rider_id).filter(phone=digits).exists():
    #         raise serializers.ValidationError("Phone number is already in use.")
    #     return digits
    
    # def validate_email(self, value):
    #     rider_id = self.instance.id if self.instance else None
    #     if RiderProfile.objects.exclude(id=rider_id).filter(email=value).exists():
    #         raise serializers.ValidationError("Email is already in use.")
    #     return value
    
    def validate(self, data):
        if self.instance is None:
            required_fields = ['name', 'email', 'phone']
            errors = {}
            for field in required_fields:
                if not data.get(field):
                    errors[field] = [f"{field.capitalize()} is required"]
            if errors:
                raise serializers.ValidationError(errors)
        return data
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.password = make_password(validated_data['password'])
            validated_data.pop('password')
        return super().update(instance, validated_data)
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, error_messages={"required": "Email is required"})
    password = serializers.CharField(write_only=True, required=True, error_messages={"required": "Password is required"})


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ['rider']


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = ['user_name', 'user_phone', 'rider', 'status']

    def validate_user_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must have 10 digits.")
        
        return value
    
    # def validate_charges(self, value):
    #     if value <= 0:
    #         raise serializers.ValidationError("Charges must be greater than 0")
    #     return value

class RiderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderPayment
        fields = '__all__'