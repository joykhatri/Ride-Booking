from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path

router = DefaultRouter()
router.register('profile', RiderProfileViewSet, basename='rider-profile')
router.register('vehicle', VehicleViewSet, basename='vehicle')
router.register('ride', RideViewSet, basename='ride')
router.register('payments', RiderPaymentViewSet, basename='payments')
router.register('ratings', RatingsViewSet, basename='ratings')

urlpatterns = [
    path('login/', LoginViewSet.as_view(), name='login')    
]

urlpatterns += router.urls