"""
FBS App Health Check Views

Views for health check and monitoring endpoints.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
import json
import time


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Basic health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'FBS App',
        'version': '2.0.0'
    })


@csrf_exempt
@require_http_methods(["GET"])
def health_status(request):
    """Detailed health status endpoint"""
    status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'FBS App',
        'version': '2.0.0',
        'components': {}
    }
    
    # Check database health
    try:
        db_conn = connections['default']
        db_conn.cursor()
        status['components']['database'] = 'healthy'
    except OperationalError:
        status['components']['database'] = 'unhealthy'
        status['status'] = 'degraded'
    
    # Check FBS app configuration
    fbs_config = getattr(settings, 'FBS_APP', {})
    if fbs_config:
        status['components']['configuration'] = 'healthy'
    else:
        status['components']['configuration'] = 'unhealthy'
        status['status'] = 'degraded'
    
    # Check if any components are unhealthy
    if any(comp == 'unhealthy' for comp in status['components'].values()):
        status['status'] = 'unhealthy'
    
    return JsonResponse(status)


@csrf_exempt
@require_http_methods(["GET"])
def database_health(request):
    """Database health check endpoint"""
    try:
        db_conn = connections['default']
        cursor = db_conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        
        return JsonResponse({
            'status': 'healthy',
            'component': 'database',
            'timestamp': time.time(),
            'details': {
                'engine': db_conn.settings_dict['ENGINE'],
                'name': db_conn.settings_dict['NAME'],
                'host': db_conn.settings_dict['HOST'],
                'port': db_conn.settings_dict['PORT']
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'component': 'database',
            'timestamp': time.time(),
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def odoo_health(request):
    """Odoo connection health check endpoint"""
    fbs_config = getattr(settings, 'FBS_APP', {})
    odoo_url = fbs_config.get('ODOO_BASE_URL', 'Not configured')
    
    # Basic configuration check
    if odoo_url == 'Not configured':
        return JsonResponse({
            'status': 'unhealthy',
            'component': 'odoo',
            'timestamp': time.time(),
            'error': 'Odoo configuration not found'
        }, status=500)
    
    # For now, just check if configuration exists
    # In a real implementation, you might want to test the actual connection
    return JsonResponse({
        'status': 'healthy',
        'component': 'odoo',
        'timestamp': time.time(),
        'details': {
            'base_url': odoo_url,
            'timeout': fbs_config.get('ODOO_TIMEOUT', 30),
            'max_retries': fbs_config.get('ODOO_MAX_RETRIES', 3)
        }
    })


@csrf_exempt
@require_http_methods(["GET"])
def cache_health(request):
    """Cache health check endpoint"""
    fbs_config = getattr(settings, 'FBS_APP', {})
    cache_enabled = fbs_config.get('CACHE_ENABLED', False)
    
    if not cache_enabled:
        return JsonResponse({
            'status': 'healthy',
            'component': 'cache',
            'timestamp': time.time(),
            'details': {
                'enabled': False,
                'message': 'Caching is disabled'
            }
        })
    
    # For now, just check if caching is configured
    # In a real implementation, you might want to test Redis/Memcached connection
    return JsonResponse({
        'status': 'healthy',
        'component': 'cache',
        'timestamp': time.time(),
        'details': {
            'enabled': True,
            'timeout': fbs_config.get('CACHE_TIMEOUT', 300),
            'redis_url': fbs_config.get('REDIS_URL', 'Not configured')
        }
    })
