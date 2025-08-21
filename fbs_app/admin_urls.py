"""
FBS App Admin URLs

URL patterns for admin interface.
"""

from django.urls import path
from django.contrib import admin

app_name = 'admin'

urlpatterns = [
    # Include Django's default admin URLs
    path('', admin.site.urls),
]
