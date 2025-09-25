"""
FBS Core API URLs

REST API endpoints for core FBS functionality.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .. import views

# Create router for core APIs
router = DefaultRouter()

# Core system endpoints
router.register(r'solutions', views.SolutionViewSet, basename='solution')
router.register(r'users', views.FBSUserViewSet, basename='fbsuser')
router.register(r'audit-logs', views.AuditLogViewSet, basename='auditlog')
router.register(r'api-tokens', views.APITokenViewSet, basename='apitoken')
router.register(r'system-settings', views.SystemSettingsViewSet, basename='systemsettings')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Authentication endpoints
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),

    # System endpoints
    path('system/info/', views.SystemInfoView.as_view(), name='system_info'),
]
