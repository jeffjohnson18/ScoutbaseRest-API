# Import the path function from the django.urls module
# Import the admin function from the django.contrib module
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Define the URL patterns for the project
# The URL patterns all begin with http://localhost:8000/
# Followed by the path listed below
urlpatterns = [
    path('scoutbase/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)