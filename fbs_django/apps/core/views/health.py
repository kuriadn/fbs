"""
FBS Health Check API Views

API endpoints for monitoring FBS system health - headless implementation.
"""
import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import time


class HealthCheckView(APIView):
    """Basic health check API view"""

    permission_classes = []

    def get(self, request):
        """Basic health check endpoint"""
        from django.utils import timezone
        from django.conf import settings

        return Response({
            'status': 'healthy',
            'service': 'FBS Django Suite',
            'version': '4.0.0',
            'timestamp': timezone.now().isoformat(),
            'environment': 'development' if settings.DEBUG else 'production',
        })


class DetailedHealthCheckView(APIView):
    """Detailed health check with component status"""

    permission_classes = []

    def get(self, request):
        """Comprehensive health check"""
        start_time = time.time()

        health_status = {
            'status': 'healthy',
            'service': 'FBS Django Suite',
            'version': '4.0.0',
            'timestamp': timezone.now().isoformat(),
            'response_time_ms': None,
            'components': {},
        }

        # Check database health
        health_status['components']['database'] = self._check_database()

        # Check cache health
        health_status['components']['cache'] = self._check_cache()

        # Check Odoo integration
        health_status['components']['odoo'] = self._check_odoo()

        # Check license system (if request has solution context)
        health_status['components']['license'] = self._check_license(request)

        # Check file system
        health_status['components']['filesystem'] = self._check_filesystem()

        # Determine overall status
        unhealthy_components = [
            comp for comp in health_status['components'].values()
            if comp.get('status') != 'healthy'
        ]

        if unhealthy_components:
            health_status['status'] = 'degraded' if len(unhealthy_components) == 1 else 'unhealthy'

        # Calculate response time
        health_status['response_time_ms'] = round((time.time() - start_time) * 1000, 2)

        response_status = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(health_status, status=response_status)

    def _check_database(self):
        """Check database connectivity and performance"""
        try:
            from django.db import connection
            start_time = time.time()

            # Execute a simple query
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            query_time = time.time() - start_time

            if result and result[0] == 1:
                return {
                    'status': 'healthy',
                    'message': 'Database connection successful',
                    'query_time_ms': round(query_time * 1000, 2),
                    'engine': connection.vendor,
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Database query failed',
                }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}',
            }

    def _check_cache(self):
        """Check cache backend health"""
        try:
            from django.core.cache import cache
            start_time = time.time()

            # Test cache set/get
            test_key = 'health_check_test'
            test_value = f'test_{time.time()}'

            cache.set(test_key, test_value, 10)
            retrieved_value = cache.get(test_key)

            cache_time = time.time() - start_time

            if retrieved_value == test_value:
                # Clean up
                cache.delete(test_key)

                return {
                    'status': 'healthy',
                    'message': 'Cache backend operational',
                    'response_time_ms': round(cache_time * 1000, 2),
                    'backend': cache.__class__.__name__,
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Cache set/get test failed',
                }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Cache backend failed: {str(e)}',
            }

    def _check_odoo(self):
        """Check Odoo integration health"""
        try:
            from django.conf import settings
            odoo_config = getattr(settings, 'ODOO_CONFIG', {})

            if not odoo_config.get('BASE_URL'):
                return {
                    'status': 'healthy',
                    'message': 'Odoo integration not configured (optional)',
                }

            # Try to import Odoo service
            try:
                from apps.odoo_integration.services import OdooService

                # Get solution for context
                solution = getattr(self.request, 'solution', None)
                if solution:
                    odoo_service = OdooService(solution)
                    health_result = odoo_service.health_check()
                else:
                    # Basic connectivity test without solution context
                    import xmlrpc.client
                    common = xmlrpc.client.ServerProxy(f"{odoo_config['BASE_URL']}/xmlrpc/2/common")
                    version = common.version()

                    health_result = {
                        'status': 'healthy',
                        'message': f'Odoo {version.get("server_version", "unknown")} connected',
                        'server_version': version.get('server_version'),
                    }

                return health_result

            except ImportError:
                return {
                    'status': 'healthy',
                    'message': 'Odoo integration module not available',
                }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Odoo health check failed: {str(e)}',
            }

    def _check_license(self, request):
        """Check license system health"""
        try:
            # Get solution context
            solution = getattr(request, 'solution', None)
            if not solution:
                return {
                    'status': 'healthy',
                    'message': 'No solution context available',
                }

            # Try to import license service
            try:
                from apps.licensing.services import LicenseService
                license_service = LicenseService(solution)

                # Check if license exists and is valid
                license_obj = license_service.get_license()

                if license_obj:
                    return {
                        'status': 'healthy' if license_obj.status == 'active' else 'warning',
                        'message': f'License {license_obj.status}',
                        'license_type': license_obj.license_type,
                        'expires_at': license_obj.expires_at.isoformat() if license_obj.expires_at else None,
                    }
                else:
                    return {
                        'status': 'warning',
                        'message': 'No license configured',
                    }

            except ImportError:
                return {
                    'status': 'healthy',
                    'message': 'License system not available',
                }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'License check failed: {str(e)}',
            }

    def _check_filesystem(self):
        """Check file system health"""
        try:
            from django.conf import settings
            import os

            # Check media directory
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if media_root and os.path.exists(media_root):
                # Check if writable
                test_file = os.path.join(media_root, '.health_check')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)

                    return {
                        'status': 'healthy',
                        'message': 'File system operational',
                        'media_root': media_root,
                    }
                except Exception as e:
                    return {
                        'status': 'unhealthy',
                        'message': f'File system not writable: {str(e)}',
                    }
            else:
                return {
                    'status': 'warning',
                    'message': 'Media directory not configured',
                }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'File system check failed: {str(e)}',
            }
