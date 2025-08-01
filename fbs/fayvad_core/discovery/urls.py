from django.urls import path
from . import views

app_name = 'fbs_discovery'

urlpatterns = [
    # Discovery Management Endpoints
    path('discoveries/<str:domain>/<str:discovery_type>/', 
         views.DiscoveryManagementView.as_view(), 
         name='discovery_management'),
    
    # Solution Management Endpoints
    path('solutions/setup/', 
         views.SolutionSetupView.as_view(), 
         name='solution_setup'),
    
    path('solutions/<str:solution_name>/status/', 
         views.SolutionStatusView.as_view(), 
         name='solution_status'),
    
    path('solutions/<str:solution_name>/migrate/', 
         views.SolutionMigrationView.as_view(), 
         name='solution_migration'),
    
    path('solutions/<str:solution_name>/discoveries/', 
         views.SolutionDiscoveryView.as_view(), 
         name='solution_discoveries'),
    
    path('solutions/', 
         views.SolutionListView.as_view(), 
         name='solution_list'),
    
    # Health Check Endpoint
    path('health/', 
         views.HealthCheckView.as_view(), 
         name='health_check'),
    
    # 2-Phase Approach Endpoints
    path('phase1/metadata/', 
         views.Phase1MetadataView.as_view(), 
         name='phase1_metadata'),
    
    path('phase2/setup/', 
         views.Phase2CompleteSetupView.as_view(), 
         name='phase2_setup'),
    
    path('solutions/<str:solution_name>/operations/', 
         views.SolutionOperationsView.as_view(), 
         name='solution_operations'),
] 