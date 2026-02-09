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
-> pip install djangorestframework-simplejwt (For JWT Authentication)
-> pip install channels (For WebSocket)

Add apps to INSTALLED_APPS in vehicle_system/settings.py:INSTALLED_APPS = [
    ...
    'rest_framework',
    'riders',
    'channels',
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

16. Pick Up Ride
    POST /api/riders/ride/{id}/pickup/

17. Decline Ride
    POST /api/riders/ride/{id}/decline/

18. Complete Ride
    POST /api/riders/ride/{id}/complete/

19. Create Payment
    POST /api/riders/payments/{id}/create_payment/

20. Payment Paid
    POST /api/riders/payments/{id}/mark_paid/


WebSocket - It check real time Riders availability.
When User book ride and rider accept, then the availabilty status is rider is automatically False and it will not show in webSocket Response, when Rider completed the ride then the availabilty status is automatically true, and it will show in WebSocket Response.

-> For WebSocket
Install daphne to runserver for asgi
-> pip install daphne   

-> For run daphne server
$env:DJANGO_SETTINGS_MODULE="project.settings"
daphne -p 8000 project.asgi:application

WebScoket Endpoints (Postman)
-> Select WebSocket in Postman
-> Enter this EndPoint (ws://127.0.0.1:8000/ws/riders/availability/) (-> This WebSocket is for to check rider availability.)

-> For Create Ride
    ws://127.0.0.1:8000/ws/riders/user_ride/?token={Access Token of Login User}

    Enter this data is Message(Ex.)
    
    {
    "action": "create_ride",
    "data": {
        "pickup_location": "street A",
        "pickup_latitude": 23.0197999,
        "pickup_longitude": 72.5268579,
        "drop_location": "street B",
        "drop_longitude": 12.858373,
        "drop_latitude": 77.600835,
        "vehicle_type": "CAR",
        "charges": 150
    }
}

-> For Create Ride WebSocket (When user create new ride, then all nearby rider can see that ride details)
    ws://127.0.0.1:8000/ws/riders/new_ride/{rider_id}

-> For Rider live location (With latitude & longitude)
    ws://127.0.0.1:8000/ws/riders/location/{rider_id}/

    Enter this data in Message & update the data then it also give response in websocket & also change values in DB.
    {
    "latitude": ,
    "longitude": 
    }
