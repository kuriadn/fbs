"""
FBS App Dashboard URLs

URL patterns for dashboard interface.
"""

from django.urls import path
from . import views as dashboard_views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', dashboard_views.dashboard_home, name='dashboard-home'),
    
    # MSME dashboard
    path('msme/', dashboard_views.msme_dashboard, name='msme-dashboard'),
    
    # Business Intelligence dashboard
    path('bi/', dashboard_views.bi_dashboard, name='bi-dashboard'),
    
    # Workflow dashboard
    path('workflows/', dashboard_views.workflow_dashboard, name='workflow-dashboard'),
    
    # Compliance dashboard
    path('compliance/', dashboard_views.compliance_dashboard, name='compliance-dashboard'),
    
    # Accounting dashboard
    path('accounting/', dashboard_views.accounting_dashboard, name='accounting-dashboard'),
]
