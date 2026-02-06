from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class RiderManager(BaseUserManager):
    def create_user(self, email, phone, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not phone:
            raise ValueError('Phone is required')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone, name, password, **extra_fields)
    
        
class RiderProfile(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, default='example@gmail.com')
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=[
        ('USER', 'User'),
        ('RIDER', 'Rider'),
        ('ADMIN', 'Admin'),
    ])
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_available= models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = RiderManager()

    def __str__(self):
        return self.name
    
class Vehicle(models.Model):
    rider = models.OneToOneField(RiderProfile, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20, choices=[
        ('BIKE', 'Bike'),
        ('CAR', 'Car'),
        ('AUTO', 'Auto')
    ])

    def __str__(self):
        return self.vehicle_number
    
class Ride(models.Model):
    rider = models.ForeignKey(RiderProfile, on_delete=models.CASCADE, null=True, blank=True)
    user_name = models.CharField(max_length=100)
    user_phone = models.CharField(max_length=20)
    pickup_location = models.CharField(max_length=250)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=7)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=7)
    drop_location = models.CharField(max_length=250)
    drop_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    drop_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    vehicle_type = models.CharField(max_length=20, choices=[
        ('CAR', 'Car'),
        ('BIKE', 'Bike'),
        ('AUTO', 'Auto')
    ])
    status = models.CharField(max_length=20, choices=[
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('declined', 'Declined'),
        ('completed', 'Completed')
    ], default='requested')
    charges = models.DecimalField(max_digits=10, decimal_places=2)
    requested_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"Ride {self.id} - {self.status}"
    
class RiderPayment(models.Model):
    ride = models.OneToOneField(Ride, on_delete=models.CASCADE)
    rider = models.ForeignKey(RiderProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Ride {self.ride.id} - Paid: {self.paid}"
