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
   GET /api/riders/profile/{id}

4. Update User
   PUT /api/riders/profile/{id}

5. Delete User
   DELETE /api/riders/profile/{id}

6. Login
   POST /api/riders/login/
   {
    "email": "",
    "password": ""
}

7. Create Vehicle
   POST /api/riders/vehicle/
   {
  "vehicle_number": "",
  "vehicle_type": ""
}

8. Get Vehicle
   GET /api/riders/vehicle/

9. Get Vehicle by Id
    GET /api/riders/vehicle/{id}

10. Update Vehicle
    PUT /api/riders/vehicle/{id}

11. Delete Vehicle
    DELETE /api/riders/vehicle/{id}

