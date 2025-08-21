"""
FBS App URL Configuration

This module defines all URL patterns for the FBS app.
Include this in your host Django project's urls.py:

    path('fbs/', include('fbs_app.urls')),
"""

from django.urls import path, include
from django.conf import settings

# Import views
from . import auth_views, health_views

# Main FBS app URLs
app_name = 'fbs_app'

urlpatterns = [
    # =============================================================================
    # AUTHENTICATION ENDPOINTS
    # =============================================================================
    
    # Handshake authentication
    path('auth/handshake/create/', auth_views.create_handshake, name='create-handshake'),
    path('auth/handshake/validate/', auth_views.validate_handshake, name='validate-handshake'),
    path('auth/handshake/revoke/', auth_views.revoke_handshake, name='revoke-handshake'),
    path('auth/handshake/list/', auth_views.list_handshakes, name='list-handshakes'),
    
    # Token management
    path('auth/tokens/create/', auth_views.create_token, name='create-token'),
    path('auth/tokens/validate/', auth_views.validate_token, name='validate-token'),
    path('auth/tokens/revoke/', auth_views.revoke_token, name='revoke-token'),
    path('auth/tokens/list/', auth_views.list_tokens, name='list-tokens'),
    
    # =============================================================================
    # HEALTH CHECK ENDPOINTS
    # =============================================================================
    
    # Basic health check
    path('health/', health_views.health_check, name='health-check'),
    
    # Detailed health status
    path('health/status/', health_views.health_status, name='health-status'),
    
    # Database health
    path('health/database/', health_views.database_health, name='database-health'),
    
    # Odoo connection health
    path('health/odoo/', health_views.odoo_health, name='odoo-health'),
    
    # Cache health
    path('health/cache/', health_views.cache_health, name='cache-health'),
    
    # =============================================================================
    # ADMIN INTERFACE (Optional)
    # =============================================================================
    
    # Admin interface - only if enabled
    path('admin/', include('fbs_app.admin_urls')),
    
    # =============================================================================
    # DASHBOARD/UI ENDPOINTS (Optional)
    # =============================================================================
    
    # Dashboard endpoints - only if frontend is included
    # path('dashboard/', include('fbs_app.dashboard_urls')),  # Commented out until dashboard views are implemented
]

# Add custom URL prefix if configured
if hasattr(settings, 'FBS_URL_PREFIX') and settings.FBS_URL_PREFIX != 'fbs/':
    # This allows host projects to customize the URL structure
    # The prefix is handled at the project level
    pass
