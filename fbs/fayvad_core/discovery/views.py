from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from .integration_service import FBSAPIIntegrationService
from .services import FBSDiscoveryService

logger = logging.getLogger(__name__)


class DiscoveryManagementView(APIView):
    """API view for discovery management"""
    permission_classes = [AllowAny]  # Can be changed to IsAuthenticated for production
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.discovery_service = FBSDiscoveryService()
    
    def get(self, request, domain, discovery_type):
        """Get cached discoveries for a domain and type"""
        try:
            discoveries = self.discovery_service.get_cached_discoveries(domain, discovery_type)
            
            return Response({
                'success': True,
                'domain': domain,
                'discovery_type': discovery_type,
                'count': len(discoveries),
                'discoveries': discoveries
            })
            
        except Exception as e:
            logger.error(f"Failed to get discoveries: {str(e)}")
            return Response({
                'success': False,
                'error': str(e),
                'domain': domain,
                'discovery_type': discovery_type
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, domain, discovery_type):
        """Force refresh of discoveries"""
        try:
            database = request.data.get('database')
            discoveries = self.discovery_service.refresh_discoveries(domain, discovery_type, database)
            
            return Response({
                'success': discoveries.get('success', False),
                'domain': domain,
                'discovery_type': discovery_type,
                'refreshed_count': discoveries.get('discovered_count', 0),
                'discoveries': discoveries.get('discoveries', []),
                'error': discoveries.get('error')
            })
            
        except Exception as e:
            logger.error(f"Failed to refresh discoveries: {str(e)}")
            return Response({
                'success': False,
                'error': str(e),
                'domain': domain,
                'discovery_type': discovery_type
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SolutionSetupView(APIView):
    """API view for solution setup"""
    permission_classes = [AllowAny]  # Can be changed to IsAuthenticated for production
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integration_service = FBSAPIIntegrationService()
    
    def post(self, request):
        """Complete solution setup"""
        try:
            solution_config = request.data
            
            # Validate configuration
            validation = self.integration_service.validate_solution_config(solution_config)
            if not validation['valid']:
                return Response({
                    'success': False,
                    'error': validation['error'],
                    'validation_details': validation
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Setup solution
            result = self.integration_service.setup_solution(solution_config)
            
            if result['success']:
                return Response({
                    'success': True,
                    'result': result
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Setup failed'),
                    'result': result
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Solution setup failed: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SolutionStatusView(APIView):
    """API view for solution status"""
    permission_classes = [AllowAny]  # Can be changed to IsAuthenticated for production
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integration_service = FBSAPIIntegrationService()
    
    def get(self, request, solution_name):
        """Get solution status"""
        try:
            status_result = self.integration_service.get_solution_status(solution_name)
            
            if status_result['success']:
                return Response({
                    'success': True,
                    'solution_name': solution_name,
                    'status': status_result
                })
            else:
                return Response({
                    'success': False,
                    'error': status_result.get('error', 'Solution not found'),
                    'solution_name': solution_name
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Failed to get solution status: {str(e)}")
            return Response({
                'success': False,
                'error': str(e),
                'solution_name': solution_name
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SolutionMigrationView(APIView):
    """API view for solution schema migration"""
    permission_classes = [AllowAny]  # Can be changed to IsAuthenticated for production
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integration_service = FBSAPIIntegrationService()
    
    def post(self, request, solution_name):
        """Migrate solution schema"""
        try:
            new_version = request.data.get('new_version')
            if not new_version:
                return Response({
                    'success': False,
                    'error': 'new_version is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            migration_result = self.integration_service.migrate_solution_schema(solution_name, new_version)
            
            if migration_result['success']:
                return Response({
                    'success': True,
                    'result': migration_result
                })
            else:
                return Response({
                    'success': False,
                    'error': migration_result.get('error', 'Migration failed'),
                    'result': migration_result
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Schema migration failed: {str(e)}")
            return Response({
                'success': False,
                'error': str(e),
                'solution_name': solution_name
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SolutionDiscoveryView(APIView):
    """API view for solution discoveries"""
    permission_classes = [AllowAny]  # Can be changed to IsAuthenticated for production
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integration_service = FBSAPIIntegrationService()
    
    def get(self, request, solution_name):
        """Get discoveries for a solution"""
        try:
            discovery_type = request.GET.get('type')  # Optional: model, workflow, bi_feature
            result = self.integration_service.get_solution_discoveries(solution_name, discovery_type)
            
            if result['success']:
                return Response({
                    'success': True,
                    'result': result
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to get discoveries'),
                    'solution_name': solution_name
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Failed to get discoveries: {str(e)}")
            return Response({
                'success': False,
                'error': str(e),
                'solution_name': solution_name
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, solution_name):
        """Refresh discoveries for a solution"""
        try:
            discovery_types = request.data.get('discovery_types')  # Optional: list of types
            result = self.integration_service.refresh_solution_discoveries(solution_name, discovery_types)
            
            if result['success']:
                return Response({
                    'success': True,
                    'result': result
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to refresh discoveries'),
                    'solution_name': solution_name
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Failed to refresh discoveries: {str(e)}")
            return Response({
                'success': False,
                'error': str(e),
                'solution_name': solution_name
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SolutionListView(APIView):
    """API view for listing solutions"""
    permission_classes = [AllowAny]  # Can be changed to IsAuthenticated for production
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integration_service = FBSAPIIntegrationService()
    
    def get(self, request):
        """List all solutions"""
        try:
            result = self.integration_service.list_solutions()
            
            if result['success']:
                return Response({
                    'success': True,
                    'solutions': result['solutions'],
                    'count': result['count']
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to list solutions')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Failed to list solutions: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Health check"""
        try:
            # Basic health check
            from .models import FBSDiscovery, FBSSolutionSchema
            
            discovery_count = FBSDiscovery.objects.filter(is_active=True).count()
            solution_count = FBSSolutionSchema.objects.filter(is_active=True).count()
            
            return Response({
                'status': 'healthy',
                'timestamp': '2024-01-15T10:30:00Z',
                'services': {
                    'discovery_service': 'operational',
                    'schema_service': 'operational',
                    'integration_service': 'operational'
                },
                'metrics': {
                    'active_discoveries': discovery_count,
                    'active_solutions': solution_count
                }
            })
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return Response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': '2024-01-15T10:30:00Z'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class Phase1MetadataView(APIView):
    """API view for Phase 1: Metadata discovery"""
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integration_service = FBSAPIIntegrationService()
    
    def get(self, request):
        """Get available modules metadata"""
        try:
            result = self.integration_service.phase1_metadata_discovery()
            
            if result['status'] == 'success':
                return Response({
                    'success': True,
                    'total_modules': result['total_modules'],
                    'module_catalog': result['module_catalog'],
                    'message': result['message']
                })
            else:
                return Response({
                    'success': False,
                    'error': result['message']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Phase 1 failed: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Phase2CompleteSetupView(APIView):
    """API view for Phase 2: Complete setup with user requirements"""
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integration_service = FBSAPIIntegrationService()
    
    def post(self, request):
        """Complete Phase 2 setup"""
        try:
            solution_config = request.data.get('solution_config', {})
            user_requirements = request.data.get('user_requirements', {})
            
            if not solution_config or not user_requirements:
                return Response({
                    'success': False,
                    'error': 'Both solution_config and user_requirements are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result = self.integration_service.phase2_complete_setup(solution_config, user_requirements)
            
            if result['status'] == 'success':
                return Response({
                    'success': True,
                    'solution_name': result['solution_name'],
                    'database': result['database'],
                    'selected_modules': result['selected_modules'],
                    'modules_installed': result['modules_installed'],
                    'discovery_results': result['discovery_results'],
                    'message': result['message']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result['message']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Phase 2 failed: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


class SolutionOperationsView(APIView):
    """API view for Phase 3: Operations on user's solution database"""
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integration_service = FBSAPIIntegrationService()
    
    def post(self, request, solution_name):
        """Perform operations on solution database"""
        try:
            operation_type = request.data.get('operation_type')
            operation_data = request.data.get('operation_data', {})
            
            if not operation_type:
                return Response({
                    'success': False,
                    'error': 'operation_type is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result = self.integration_service.solution_operations(solution_name, operation_type, operation_data)
            
            if result['status'] == 'success':
                return Response({
                    'success': True,
                    'solution_name': solution_name,
                    'operation': operation_type,
                    'result': result
                })
            else:
                return Response({
                    'success': False,
                    'error': result['message']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Solution operation failed: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 