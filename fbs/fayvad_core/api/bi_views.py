"""
Business Intelligence API Views

RESTful API endpoints for BI capabilities including:
- Analytics data retrieval
- Report generation
- Dashboard data
- KPI calculations
"""

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from ..services.bi_service import bi_service
from ..auth.drf_auth import JWTAuthentication
import logging
from django.utils import timezone

logger = logging.getLogger('fayvad_core.api.bi')


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def analytics_data(request):
    """Get analytics data for a model"""
    
    try:
        # Extract parameters
        model_name = request.GET.get('model')
        report_type = request.GET.get('report_type', 'summary')
        database = request.GET.get('db')
        
        if not model_name or not database:
            return Response({
                'success': False,
                'error': 'model and db parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse filters from query parameters
        filters = {}
        for key, value in request.GET.items():
            if key.startswith('filter_'):
                filter_key = key[7:]  # Remove 'filter_' prefix
                filters[filter_key] = value
        
        # Parse group_by and measures
        group_by = request.GET.getlist('group_by')
        measures = request.GET.getlist('measures')
        
        # Parse date range
        date_range = {}
        if request.GET.get('date_from'):
            date_range['from'] = request.GET.get('date_from')
        if request.GET.get('date_to'):
            date_range['to'] = request.GET.get('date_to')
        
        # Get analytics data
        result = bi_service.get_analytics_data(
            model_name=model_name,
            token=request.auth,
            database=database,
            report_type=report_type,
            filters=filters,
            group_by=group_by,
            measures=measures,
            date_range=date_range
        )
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error getting analytics data: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sales_report(request):
    """Generate sales report"""
    
    try:
        # Extract parameters
        period = request.GET.get('period', 'month')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        database = request.GET.get('db')
        
        if not database:
            return Response({
                'success': False,
                'error': 'db parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate sales report
        result = bi_service.generate_sales_report(
            token=request.auth,
            database=database,
            period=period,
            date_from=date_from,
            date_to=date_to
        )
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error generating sales report: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def inventory_report(request):
    """Generate inventory report"""
    
    try:
        # Extract parameters
        database = request.GET.get('db')
        
        if not database:
            return Response({
                'success': False,
                'error': 'db parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate inventory report
        result = bi_service.generate_inventory_report(
            token=request.auth,
            database=database
        )
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error generating inventory report: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def dashboard_data(request, dashboard_type):
    """Get dashboard data"""
    
    try:
        # Extract parameters
        database = request.GET.get('db')
        
        if not database:
            return Response({
                'success': False,
                'error': 'db parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate dashboard type
        valid_types = ['sales', 'inventory', 'financial', 'operations']
        if dashboard_type not in valid_types:
            return Response({
                'success': False,
                'error': f'Invalid dashboard type. Must be one of: {", ".join(valid_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get dashboard data
        result = bi_service.get_dashboard_data(
            dashboard_type=dashboard_type,
            token=request.auth,
            database=database,
            user=request.user
        )
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def kpi_summary(request):
    """Get KPI summary for all dashboards"""
    
    try:
        # Extract parameters
        database = request.GET.get('db')
        
        if not database:
            return Response({
                'success': False,
                'error': 'db parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get KPI data from all dashboards
        kpi_data = {}
        
        # Sales KPIs
        sales_dashboard = bi_service.get_dashboard_data('sales', request.auth, database, request.user)
        if sales_dashboard.get('success'):
            kpi_data['sales'] = sales_dashboard.get('dashboard', {}).get('kpis', {})
        
        # Inventory KPIs
        inventory_dashboard = bi_service.get_dashboard_data('inventory', request.auth, database, request.user)
        if inventory_dashboard.get('success'):
            kpi_data['inventory'] = inventory_dashboard.get('dashboard', {}).get('kpis', {})
        
        # Financial KPIs
        financial_dashboard = bi_service.get_dashboard_data('financial', request.auth, database, request.user)
        if financial_dashboard.get('success'):
            kpi_data['financial'] = financial_dashboard.get('dashboard', {}).get('kpis', {})
        
        # Operations KPIs
        operations_dashboard = bi_service.get_dashboard_data('operations', request.auth, database, request.user)
        if operations_dashboard.get('success'):
            kpi_data['operations'] = operations_dashboard.get('dashboard', {}).get('kpis', {})
        
        return Response({
            'success': True,
            'data': {
                'kpis': kpi_data,
                'timestamp': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting KPI summary: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def available_reports(request):
    """List available reports"""
    
    try:
        # Extract parameters
        database = request.GET.get('db')
        model = request.GET.get('model')
        
        if not database:
            return Response({
                'success': False,
                'error': 'db parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get reports from Odoo
        from ..services.odoo_client import odoo_client
        
        result = odoo_client.list_reports(
            token=request.auth,
            database=database,
            model=model
        )
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def execute_report(request):
    """Execute a specific report"""
    
    try:
        # Extract parameters
        report_id = request.data.get('report_id')
        database = request.data.get('db')
        parameters = request.data.get('parameters', {})
        format_type = request.data.get('format', 'json')
        
        if not report_id or not database:
            return Response({
                'success': False,
                'error': 'report_id and db are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Execute report via Odoo
        from ..services.odoo_client import odoo_client
        
        result = odoo_client.execute_report(
            report_id=report_id,
            token=request.auth,
            database=database,
            parameters=parameters,
            format=format_type
        )
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error executing report: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def available_dashboards(request):
    """List available dashboards"""
    
    try:
        # Extract parameters
        database = request.GET.get('db')
        
        if not database:
            return Response({
                'success': False,
                'error': 'db parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get dashboards from Odoo
        from ..services.odoo_client import odoo_client
        
        result = odoo_client.list_dashboards(
            token=request.auth,
            database=database
        )
        
        # Add built-in dashboards
        built_in_dashboards = [
            {
                'id': 'sales',
                'name': 'Sales Dashboard',
                'type': 'built_in',
                'description': 'Sales performance and analytics'
            },
            {
                'id': 'inventory',
                'name': 'Inventory Dashboard',
                'type': 'built_in',
                'description': 'Inventory management and stock levels'
            },
            {
                'id': 'financial',
                'name': 'Financial Dashboard',
                'type': 'built_in',
                'description': 'Financial performance and metrics'
            },
            {
                'id': 'operations',
                'name': 'Operations Dashboard',
                'type': 'built_in',
                'description': 'Operational activities and workflows'
            }
        ]
        
        # Combine Odoo dashboards with built-in ones
        if result.get('success'):
            odoo_dashboards = result.get('data', [])
            all_dashboards = built_in_dashboards + odoo_dashboards
        else:
            all_dashboards = built_in_dashboards
        
        return Response({
            'success': True,
            'data': all_dashboards
        })
        
    except Exception as e:
        logger.error(f"Error listing dashboards: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def dashboard_widgets(request, dashboard_id):
    """Get dashboard widgets data"""
    
    try:
        # Extract parameters
        database = request.GET.get('db')
        
        if not database:
            return Response({
                'success': False,
                'error': 'db parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if it's a built-in dashboard
        built_in_dashboards = ['sales', 'inventory', 'financial', 'operations']
        
        if dashboard_id in built_in_dashboards:
            # Get built-in dashboard data
            result = bi_service.get_dashboard_data(
                dashboard_type=dashboard_id,
                token=request.auth,
                database=database,
                user=request.user
            )
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'data': {
                        'dashboard_id': dashboard_id,
                        'type': 'built_in',
                        'widgets': result.get('dashboard', {})
                    }
                })
            else:
                return Response(result)
        else:
            # Get dashboard from Odoo
            from ..services.odoo_client import odoo_client
            
            result = odoo_client.get_dashboard_data(
                dashboard_id=int(dashboard_id),
                token=request.auth,
                database=database
            )
            
            return Response(result)
        
    except Exception as e:
        logger.error(f"Error getting dashboard widgets: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 