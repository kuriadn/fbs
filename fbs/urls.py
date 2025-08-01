from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('fbs.fayvad_core.auth.urls')),
    path('api/', include('api.urls')),
    path('health/', include('fbs.fayvad_core.health.urls')),
] 