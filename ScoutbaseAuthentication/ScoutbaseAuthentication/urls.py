# Import the path function from the django.urls module
# Import the admin function from the django.contrib module
from django.contrib import admin
from django.urls import path, include

# Define the URL patterns for the project
# The URL patterns all begin with http://localhost:8000/
# Followed by the path listed below
urlpatterns = [
    path('scoutbase/', include('users.urls')),
]
