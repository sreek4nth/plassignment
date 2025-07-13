from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),     # Django admin
    path('', include('core.urls')),      # Includes all views from core app
]
