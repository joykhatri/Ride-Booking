Create virtual environment.
-> python -m venv .venv

Activate virtual environment.
-> .venv\Scripts\activate

for server run.
-> python manage.py runserver

install django, django rest framework & MySQL.
-> pip install django djangorestframework
-> pip install mysqlclient
-> django-admin startproject project .
-> django-admin startapp riders
-> pip install djangorestframework-simplejwt

Add apps to INSTALLED_APPS in vehicle_system/settings.py:INSTALLED_APPS = [
    ...
    'rest_framework',
    'riders',
]

-> After install mysql
Add this to settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'DB_NAME',
        'USER': 'DB_USER',
        'PASSWORD': 'DB_PASSWORD',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

after creating model.py
python manage.py makemigrations
python manage.py migrate


for runserver
python manage.py runserver

for APIs testing - Postman

APIs endpoint:
1. Create User
   POST /api/riders/profile/
   {
    "name": "",
    "email": "",
    "phone": "",
    "password": "",
    "role": ""
}

2. Get User
   GET /api/riders/profile/

3. Get User by Id
   GET /api/riders/profile/{id}/

4. Update User
   PUT /api/riders/profile/{id}/

5. Delete User
   DELETE /api/riders/profile/{id}/

6. Login
   POST /api/riders/login/
   {
    "email": "",
    "password": ""
}

after login you have get 2 tokens (access & refresh).
enter access token in authorization (Auth Type - Bearer Token)

7. Create Vehicle
   POST /api/riders/vehicle/
   {
  "vehicle_number": "",
  "vehicle_type": ""
}

8. Get Vehicle
   GET /api/riders/vehicle/

9. Get Vehicle by Id
    GET /api/riders/vehicle/{id}/

10. Update Vehicle
    PUT /api/riders/vehicle/{id}/

11. Delete Vehicle
    DELETE /api/riders/vehicle/{id}/

12. Create Ride
    POST /api/riders/ride/
    {
    "pickup_location": "street A",
    "pickup_latitude": 12.971598,
    "pickup_longitude": 77.594566,
    "drop_location": "street B",
    "drop_longitude": 12.978373,
    "drop_latitude": 77.640835,
    "vehicle_type": "CAR",
    "charges": 150
}

13. Update Ride
    PUT /api/riders/ride/{id}/

14. Delete Ride
    DELETE /api/riders/ride/{id}/

15. Accept Ride
    POST /api/riders/ride/{id}/accept/

16. Decline Ride
    POST /api/riders/ride/{id}/decline/

17. Complete Ride
    POST /api/riders/ride/{id}/complete/

18. Create Payment
    POST /api/riders/payments/{id}/create_payment/

19. Payment Paid
    POST /api/riders/payments/{id}/mark_paid/
