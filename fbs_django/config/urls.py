"""
URL configuration for FBS (Fayvad Business Suite) v4.0.0

Complete URL routing for Django-based FBS with multi-tenant architecture.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API Endpoints (Headless FBS - APIs only)
    path('api/', include([
        path('core/', include('apps.core.urls')),
        path('dms/', include('apps.dms.urls')),
        path('license/', include('apps.licensing.urls')),
        path('module-gen/', include('apps.module_gen.urls')),
        path('odoo/', include('apps.odoo_integration.urls')),
        path('discovery/', include('apps.discovery.urls')),
        path('virtual-fields/', include('apps.virtual_fields.urls')),
        path('msme/', include('apps.msme.urls')),
        path('bi/', include('apps.bi.urls')),
        path('workflows/', include('apps.workflows.urls')),
        path('compliance/', include('apps.compliance.urls')),
        path('accounting/', include('apps.accounting.urls')),
        path('auth/', include('apps.auth_handshake.urls')),
        path('onboarding/', include('apps.onboarding.urls')),
        path('notifications/', include('apps.notifications.urls')),
    ])),

    # Health Check (always available)
    path('health/', include('apps.core.urls_health')),
]

# Static and Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # API Docs in development
    urlpatterns += [
        path('api/docs/', include('rest_framework.urls')),
    ]