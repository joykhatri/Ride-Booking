This project is a Ride Booking backend built with Django, Django REST Framework, and MySQL. It supports user management, rides, vehicles, payments, JWT authentication, and real-time WebSocket updates for rider availability.

🚀 Setup Instructions
1. Create Virtual Environment
python -m venv .venv

2. Activate Virtual Environment
Windows:
.venv\Scripts\activate

Linux/macOS:
source .venv/bin/activate

3. Install Dependencies
pip install django djangorestframework mysqlclient
pip install djangorestframework-simplejwt     # JWT Authentication
pip install channels                          # WebSocket support
pip install daphne                            # ASGI server for WebSocket

4. Start Django Project & App
django-admin startproject project .
django-admin startapp riders

5. Update INSTALLED_APPS in project/settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'riders',
    'channels',
]

6. Configure MySQL Database in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'DB_NAME',
        'USER': 'DB_USER',
        'PASSWORD': 'DB_PASSWORD',
        'HOST': 'localhost',   # Or your DB host
        'PORT': '3306',
    }
}

7. Apply Migrations
python manage.py makemigrations
python manage.py migrate

8. Run Server
Development server:
python manage.py runserver


ASGI/Daphne server (for WebSocket):
$env:DJANGO_SETTINGS_MODULE="project.settings"   # Windows PowerShell
daphne -p 8000 project.asgi:application

🔑 API Endpoints

User Management
| Method | Endpoint                    | Description    |
| ------ | --------------------------- | -------------- |
| POST   | `/api/riders/profile/`      | Create user    |
| GET    | `/api/riders/profile/`      | Get all users  |
| GET    | `/api/riders/profile/{id}/` | Get user by ID |
| PUT    | `/api/riders/profile/{id}/` | Update user    |
| DELETE | `/api/riders/profile/{id}/` | Delete user    |

1. Create User
   {
    "name": "",
    "email": "",
    "phone": "",
    "password": "",
    "role": ""
}


Login
POST /api/riders/login/
{
  "email": "",
  "password": ""
}
-> Returns access and refresh tokens
-> Use access token for Bearer Authentication in protected endpoints

Vehicle Management
| Method | Endpoint                    | Description       |
| ------ | --------------------------- | ----------------- |
| POST   | `/api/riders/vehicle/`      | Create vehicle    |
| GET    | `/api/riders/vehicle/`      | List vehicles     |
| GET    | `/api/riders/vehicle/{id}/` | Get vehicle by ID |
| PUT    | `/api/riders/vehicle/{id}/` | Update vehicle    |
| DELETE | `/api/riders/vehicle/{id}/` | Delete vehicle    |

Create Vehicle
{
  "vehicle_number": "",
  "vehicle_type": ""
}

Ride Management
| Method | Endpoint                          | Description   |
| ------ | --------------------------------- | ------------- |
| POST   | `/api/riders/ride/`               | Create ride   |
| PUT    | `/api/riders/ride/{id}/`          | Update ride   |
| DELETE | `/api/riders/ride/{id}/`          | Delete ride   |
| POST   | `/api/riders/ride/{id}/accept/`   | Accept ride   |
| POST   | `/api/riders/ride/{id}/pickup/`   | Pick up ride  |
| POST   | `/api/riders/ride/{id}/decline/`  | Decline ride  |
| POST   | `/api/riders/ride/{id}/complete/` | Complete ride |

Create Ride
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

Payment Management
| Method | Endpoint                                    | Description          |
| ------ | ------------------------------------------- | -------------------- |
| POST   | `/api/riders/payments/{id}/create_payment/` | Create payment       |
| POST   | `/api/riders/payments/{id}/mark_paid/`      | Mark payment as paid |


🌐 WebSocket Endpoints
Check Rider Availability
ws://127.0.0.1:8000/ws/riders/availability/{user_id}

Send:
{
  "latitude": 23.053420,
  "longitude": 72.521230
}
Returns nearby riders within 5 km.

User Ride Events (Create Ride)
ws://127.0.0.1:8000/ws/riders/user_ride/{user_id}/

Create ride example:
{
  "action": "create_ride",
  "data": {
    "pickup_location": "street A",
    "pickup_latitude": 23.0197999,
    "pickup_longitude": 72.5268579,
    "drop_location": "street B",
    "drop_latitude": 77.600835,
    "drop_longitude": 12.858373,
    "vehicle_type": 1,
    "charges": 150
  }
}

Notify Nearby Riders of New Ride
ws://127.0.0.1:8000/ws/riders/new_ride/{rider_id}

Rider Live Location Updates
ws://127.0.0.1:8000/ws/riders/location/{rider_id}/

Send:
{
  "latitude": 23.0197999,
  "longitude": 72.5268579
}
Updates DB and broadcasts new location in real-time.

⚡ WebSocket Notes
Riders availability updates automatically when ride is accepted/completed.
Only available riders appear in WebSocket responses for nearby users.
