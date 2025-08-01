from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GenericModelViewSet,
    DatabaseViewSet,
    TokenMappingViewSet,
    BusinessLogicViewSet,
    ProfileViewSet,
    HealthViewSet,
    OnboardingViewSet
)
from .workflow_views import (
    workflow_definitions,
    workflow_definition_detail,
    workflow_instances,
    workflow_instance_detail,
    workflow_transitions,
    workflow_actions
)
from .bi_views import (
    analytics_data,
    sales_report,
    inventory_report,
    dashboard_data,
    kpi_summary,
    available_reports,
    execute_report,
    available_dashboards,
    dashboard_widgets
)

router = DefaultRouter()
router.register(r'databases', DatabaseViewSet, basename='database')
router.register(r'tokens', TokenMappingViewSet, basename='token')
router.register(r'business', BusinessLogicViewSet, basename='business')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'admin', OnboardingViewSet, basename='admin')

urlpatterns = [
    path('', include(router.urls)),
    path('v1/<str:model_name>/', GenericModelViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='generic-model-list'),
    path('v1/<str:model_name>/<int:pk>/', GenericModelViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='generic-model-detail'),
    
    # Workflow endpoints
    path('workflows/definitions/', workflow_definitions, name='workflow-definitions'),
    path('workflows/definitions/<uuid:workflow_id>/', workflow_definition_detail, name='workflow-definition-detail'),
    path('workflows/instances/', workflow_instances, name='workflow-instances'),
    path('workflows/instances/<uuid:instance_id>/', workflow_instance_detail, name='workflow-instance-detail'),
    path('workflows/definitions/<uuid:workflow_id>/transitions/', workflow_transitions, name='workflow-transitions'),
    path('workflows/actions/', workflow_actions, name='workflow-actions'),
    
    # Business Intelligence endpoints
    path('bi/analytics/', analytics_data, name='analytics-data'),
    path('bi/reports/sales/', sales_report, name='sales-report'),
    path('bi/reports/inventory/', inventory_report, name='inventory-report'),
    path('bi/dashboards/<str:dashboard_type>/', dashboard_data, name='dashboard-data'),
    path('bi/kpi-summary/', kpi_summary, name='kpi-summary'),
    path('bi/reports/', available_reports, name='available-reports'),
    path('bi/reports/execute/', execute_report, name='execute-report'),
    path('bi/dashboards/', available_dashboards, name='available-dashboards'),
    path('bi/dashboards/<str:dashboard_id>/widgets/', dashboard_widgets, name='dashboard-widgets'),
]
