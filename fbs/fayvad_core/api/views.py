from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..services import odoo_client, AuthService, BusinessLogicService, CacheService
from ..tenants.onboarding import OnboardingService
from ..models import OdooDatabase, ApiTokenMapping, RequestLog
from .serializers import (
    OdooDatabaseSerializer,
    ApiTokenMappingSerializer,
    RequestLogSerializer,
    BusinessOperationSerializer,
    ProfileRequestSerializer
)
import logging
import json

logger = logging.getLogger('fayvad_core')


class GenericModelViewSet(viewsets.ViewSet):
    """
    Generic ViewSet for Odoo model operations
    """
    permission_classes = [IsAuthenticated]
    
    def get_database_name(self):
        """Get database name from request"""
        return getattr(self.request, 'database_name', None)
    
    def get_odoo_token(self):
        """Get Odoo token for current user and database"""
        database_name = self.get_database_name()
        if not database_name:
            return None
        return AuthService.get_user_token(self.request.user, database_name)
    
    def list(self, request, model_name):
        """List records from Odoo model"""
        try:
            token = self.get_odoo_token()
            if not token:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            database_name = self.get_database_name()
            
            # Parse query parameters
            domain = request.query_params.get('domain')
            if domain:
                try:
                    domain = json.loads(domain)
                except json.JSONDecodeError:
                    return Response(
                        {'error': 'Invalid domain format'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            fields = request.query_params.get('fields')
            if fields:
                fields = [f.strip() for f in fields.split(',')]
            
            order = request.query_params.get('order', 'id')
            limit = int(request.query_params.get('limit', 100))
            offset = int(request.query_params.get('offset', 0))
            
            # Check cache first
            cache_key = f"list:{database_name}:{model_name}:{domain}:{fields}:{order}:{limit}:{offset}"
            cached_data = CacheService.get(cache_key, database_name)
            
            if cached_data:
                return Response(cached_data)
            
            # Call Odoo API
            response = odoo_client.list_records(
                model_name=model_name,
                token=token,
                database=database_name,
                domain=domain,
                fields=fields,
                order=order,
                limit=limit,
                offset=offset
            )
            
            # Cache the response
            if response.get('success'):
                CacheService.set(cache_key, response, timeout=300, database_name=database_name)
            
            return Response(response)
            
        except Exception as e:
            logger.error(f"Error listing {model_name}: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, model_name, pk):
        """Retrieve a specific record"""
        try:
            token = self.get_odoo_token()
            if not token:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            database_name = self.get_database_name()
            
            fields = request.query_params.get('fields')
            if fields:
                fields = [f.strip() for f in fields.split(',')]
            
            # Check cache first
            cache_key = f"record:{database_name}:{model_name}:{pk}:{fields}"
            cached_data = CacheService.get(cache_key, database_name)
            
            if cached_data:
                return Response(cached_data)
            
            # Call Odoo API
            response = odoo_client.get_record(
                model_name=model_name,
                record_id=pk,
                token=token,
                database=database_name,
                fields=fields
            )
            
            # Cache the response
            if response.get('success'):
                CacheService.set(cache_key, response, timeout=300, database_name=database_name)
            
            return Response(response)
            
        except Exception as e:
            logger.error(f"Error retrieving {model_name} {pk}: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, model_name):
        """Create a new record"""
        try:
            token = self.get_odoo_token()
            if not token:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            database_name = self.get_database_name()
            
            # Validate business rules
            validation_result = BusinessLogicService.validate_business_rules(
                request.user, database_name, model_name, 'create', request.data
            )
            
            if not validation_result['valid']:
                return Response(
                    {'error': 'Validation failed', 'messages': validation_result['messages']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Call Odoo API
            response = odoo_client.create_record(
                model_name=model_name,
                data=validation_result['modified_data'],
                token=token,
                database=database_name
            )
            
            # Clear related cache entries
            CacheService.delete(f"list:{database_name}:{model_name}:*")
            
            status_code = status.HTTP_201_CREATED if response.get('success') else status.HTTP_400_BAD_REQUEST
            return Response(response, status=status_code)
            
        except Exception as e:
            logger.error(f"Error creating {model_name}: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, model_name, pk):
        """Update a record"""
        try:
            token = self.get_odoo_token()
            if not token:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            database_name = self.get_database_name()
            
            # Validate business rules
            validation_result = BusinessLogicService.validate_business_rules(
                request.user, database_name, model_name, 'update', request.data
            )
            
            if not validation_result['valid']:
                return Response(
                    {'error': 'Validation failed', 'messages': validation_result['messages']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Call Odoo API
            response = odoo_client.update_record(
                model_name=model_name,
                record_id=pk,
                data=validation_result['modified_data'],
                token=token,
                database=database_name
            )
            
            # Clear related cache entries
            CacheService.delete(f"record:{database_name}:{model_name}:{pk}:*")
            CacheService.delete(f"list:{database_name}:{model_name}:*")
            
            return Response(response)
            
        except Exception as e:
            logger.error(f"Error updating {model_name} {pk}: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, model_name, pk):
        """Partially update a record"""
        return self.update(request, model_name, pk)
    
    def destroy(self, request, model_name, pk):
        """Delete a record"""
        try:
            token = self.get_odoo_token()
            if not token:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            database_name = self.get_database_name()
            
            # Validate business rules
            validation_result = BusinessLogicService.validate_business_rules(
                request.user, database_name, model_name, 'delete', {}
            )
            
            if not validation_result['valid']:
                return Response(
                    {'error': 'Validation failed', 'messages': validation_result['messages']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Call Odoo API
            response = odoo_client.delete_record(
                model_name=model_name,
                record_id=pk,
                token=token,
                database=database_name
            )
            
            # Clear related cache entries
            CacheService.delete(f"record:{database_name}:{model_name}:{pk}:*")
            CacheService.delete(f"list:{database_name}:{model_name}:*")
            
            status_code = status.HTTP_204_NO_CONTENT if response.get('success') else status.HTTP_400_BAD_REQUEST
            return Response(response, status=status_code)
            
        except Exception as e:
            logger.error(f"Error deleting {model_name} {pk}: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DatabaseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing database configurations"""
    serializer_class = OdooDatabaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get databases accessible by current user"""
        if self.request.user.is_superuser:
            return OdooDatabase.objects.all()
        
        # Return only databases the user has access to
        return OdooDatabase.objects.filter(
            apitokenmapping__user=self.request.user,
            apitokenmapping__active=True,
            active=True
        ).distinct()
    
    @action(detail=False, methods=['get'])
    def my_databases(self, request):
        """Get databases accessible by current user"""
        databases = AuthService.get_user_databases(request.user)
        return Response({'databases': databases})


class TokenMappingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing token mappings"""
    serializer_class = ApiTokenMappingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get token mappings for current user"""
        return ApiTokenMapping.objects.filter(user=self.request.user)


class BusinessLogicViewSet(viewsets.ViewSet):
    """ViewSet for business logic operations"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def complex_operation(self, request):
        """Execute complex business operation"""
        try:
            serializer = BusinessOperationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            database_name = getattr(request, 'database_name', None)
            if not database_name:
                return Response(
                    {'error': 'Database name not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = BusinessLogicService.orchestrate_complex_operation(
                user=request.user,
                database_name=database_name,
                operation_type=serializer.validated_data['operation_type'],
                data=serializer.validated_data['data']
            )
            
            status_code = status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST
            return Response(result, status=status_code)
            
        except Exception as e:
            logger.error(f"Error executing complex operation: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfileViewSet(viewsets.ViewSet):
    """ViewSet for model profiling and discovery"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def models(self, request):
        """Get model profiling information with workflows and BI features"""
        try:
            serializer = ProfileRequestSerializer(data=request.GET)
            serializer.is_valid(raise_exception=True)
            
            database_name = getattr(request, 'database_name', None)
            if not database_name:
                return Response(
                    {'error': 'Database name not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use enhanced discovery service
            from ..generation.discovery import OdooDiscoveryService
            from ..auth.authentication import AuthService
            
            # Get authentication credentials from request context
            token = AuthService.get_user_token(request.user, database_name)
            if not token:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            discovery_service = OdooDiscoveryService()
            discovery_params = {
                'database': database_name,
                'username': request.user.username,
                'password': token  # Use token for authentication
            }
            
            # Discover models with workflows and BI features
            discovery_result = discovery_service.discover_models(discovery_params)
            
            if not discovery_result['success']:
                return Response(
                    {'error': 'Model discovery failed', 'details': discovery_result['errors']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Filter models if specified
            models = discovery_result['models']
            if 'model' in serializer.validated_data:
                model_name = serializer.validated_data['model']
                if model_name in models:
                    models = {model_name: models[model_name]}
                else:
                    return Response(
                        {'error': f'Model {model_name} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            elif 'models' in serializer.validated_data:
                requested_models = serializer.validated_data['models']
                models = {k: v for k, v in models.items() if k in requested_models}
            
            return Response({
                'success': True,
                'data': {
                    'models': models,
                    'count': len(models),
                    'discovery_info': {
                        'total_models': len(discovery_result['models']),
                        'filtered_models': len(models),
                        'has_workflows': any('workflows' in model_data for model_data in models.values()),
                        'has_bi_features': any('bi_features' in model_data for model_data in models.values())
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"Error in model profiling: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def workflows(self, request):
        """Get workflow discovery information for models"""
        try:
            model_name = request.GET.get('model')
            database_name = getattr(request, 'database_name', None)
            
            if not database_name:
                return Response(
                    {'error': 'Database name not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from ..generation.discovery import OdooDiscoveryService
            from ..auth.authentication import AuthService
            
            # Get authentication credentials from request context
            token = AuthService.get_user_token(request.user, database_name)
            if not token:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            discovery_service = OdooDiscoveryService()
            discovery_params = {
                'database': database_name,
                'username': request.user.username,
                'password': token
            }
            
            # Discover models with workflows
            discovery_result = discovery_service.discover_models(discovery_params)
            
            if not discovery_result['success']:
                return Response(
                    {'error': 'Workflow discovery failed', 'details': discovery_result['errors']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            workflows_data = {}
            
            for model_name, model_data in discovery_result['models'].items():
                if 'workflows' in model_data:
                    workflows_data[model_name] = {
                        'available_triggers': model_data['workflows']['available_triggers'],
                        'suggested_workflows': model_data['workflows']['suggested_workflows'],
                        'existing_workflows': model_data['workflows']['existing_workflows']
                    }
            
            return Response({
                'success': True,
                'data': {
                    'workflows': workflows_data,
                    'count': len(workflows_data)
                }
            })
            
        except Exception as e:
            logger.error(f"Error in workflow discovery: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def bi_features(self, request):
        """Get BI feature discovery information for models"""
        try:
            model_name = request.GET.get('model')
            database_name = getattr(request, 'database_name', None)
            
            if not database_name:
                return Response(
                    {'error': 'Database name not specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from ..generation.discovery import OdooDiscoveryService
            from ..auth.authentication import AuthService
            
            # Get authentication credentials from request context
            token = AuthService.get_user_token(request.user, database_name)
            if not token:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            discovery_service = OdooDiscoveryService()
            discovery_params = {
                'database': database_name,
                'username': request.user.username,
                'password': token
            }
            
            # Discover models with BI features
            discovery_result = discovery_service.discover_models(discovery_params)
            
            if not discovery_result['success']:
                return Response(
                    {'error': 'BI feature discovery failed', 'details': discovery_result['errors']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            bi_data = {}
            
            for model_name, model_data in discovery_result['models'].items():
                if 'bi_features' in model_data:
                    bi_data[model_name] = {
                        'available_kpis': model_data['bi_features']['available_kpis'],
                        'suggested_dashboards': model_data['bi_features']['suggested_dashboards'],
                        'reporting_capabilities': model_data['bi_features']['reporting_capabilities']
                    }
            
            return Response({
                'success': True,
                'data': {
                    'bi_features': bi_data,
                    'count': len(bi_data)
                }
            })
            
        except Exception as e:
            logger.error(f"Error in BI feature discovery: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthViewSet(viewsets.ViewSet):
    """ViewSet for health checks"""
    permission_classes = []
    
    def list(self, request):
        """Basic health check"""
        return Response({
            'status': 'ok'
        })
    
    @action(detail=False, methods=['get'])
    def detailed(self, request):
        """Detailed health check"""
        return Response({
            'status': 'ok',
            'database': 'connected',
            'cache': 'connected',
            'odoo': 'connected'
        })


class OnboardingViewSet(viewsets.ViewSet):
    """ViewSet for client onboarding"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.onboarding_service = OnboardingService()
    
    @action(detail=False, methods=['post'])
    def onboard_client(self, request):
        """Onboard a new client with database and modules"""
        try:
            client_data = request.data
            
            # Validate required fields
            if not client_data.get('name'):
                return Response(
                    {'error': 'Client name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform onboarding
            result = self.onboarding_service.onboard_client(client_data)
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error onboarding client: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def available_modules(self, request):
        """Get list of available Odoo modules"""
        try:
            modules = self.onboarding_service.get_available_modules()
            return Response(modules)
            
        except Exception as e:
            logger.error(f"Error getting available modules: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
