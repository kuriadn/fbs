"""
FBS Project URL Configuration

Main URL routing for the FBS project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # FBS App URLs - all FBS functionality under /fbs/
    path('fbs/', include('fbs_app.urls')),
]

# Add custom URL prefix if configured
if hasattr(settings, 'FBS_URL_PREFIX') and settings.FBS_URL_PREFIX != 'fbs/':
    # Replace the default FBS prefix
    fbs_prefix = settings.FBS_URL_PREFIX.rstrip('/')
    urlpatterns = [
        path(f'{fbs_prefix}/', include('fbs_app.urls')),
    ] + [url for url in urlpatterns if not url.pattern.match('fbs/')]

# Development-specific URLs (only in DEBUG mode)
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.FBS_STATIC_URL, document_root=settings.FBS_STATIC_ROOT)
    urlpatterns += static(settings.FBS_MEDIA_URL, document_root=settings.FBS_MEDIA_ROOT)
