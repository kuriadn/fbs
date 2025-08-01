from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from .authentication import TokenManager
import xmlrpc.client
import logging

logger = logging.getLogger(__name__)

class LoginView(APIView):
    """Authentication endpoint for user login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            database = request.data.get('database')
            
            if not all([username, password, database]):
                return Response({
                    'error': 'Missing required fields: username, password, database'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # First authenticate with Django
            django_user = authenticate(username=username, password=password)
            if not django_user:
                return Response({
                    'error': 'Invalid Django credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Then authenticate with Odoo
            try:
                odoo_url = getattr(settings, 'ODOO_BASE_URL', 'http://localhost:8069')
                common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
                uid = common.authenticate(database, username, password, {})
                
                if not uid:
                    return Response({
                        'error': 'Invalid Odoo credentials'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Get user permissions from Odoo
                object_client = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')
                user_data = object_client.execute_kw(database, uid, password, 'res.users', 'read', [uid], {
                    'fields': ['name', 'login', 'groups_id']
                })[0]
                
                # Get user groups and permissions
                group_ids = user_data.get('groups_id', [])
                permissions = self._get_user_permissions(database, uid, password, object_client, group_ids)
                
                # Generate JWT token
                token_manager = TokenManager(settings.JWT_SECRET_KEY)
                token = token_manager.generate_token(
                    client_id=database,
                    user_id=uid,
                    permissions=permissions,
                    expires_hours=settings.JWT_EXPIRATION_HOURS
                )
                
                return Response({
                    'success': True,
                    'token': token,
                    'user': {
                        'id': uid,
                        'name': user_data.get('name'),
                        'login': user_data.get('login'),
                        'database': database,
                        'permissions': permissions
                    },
                    'expires_in': settings.JWT_EXPIRATION_HOURS * 3600
                })
                
            except Exception as e:
                logger.error(f"Odoo authentication error: {e}")
                return Response({
                    'error': 'Odoo authentication failed'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_user_permissions(self, database, uid, password, object_client, group_ids):
        """Get user permissions based on groups"""
        try:
            # Get group data
            groups = object_client.execute_kw(database, uid, password, 'res.groups', 'read', group_ids, {
                'fields': ['name', 'category_id']
            })
            
            permissions = {}
            
            # Map groups to permissions (simplified mapping)
            for group in groups:
                group_name = group.get('name', '').lower()
                category = group.get('category_id', [False, ''])[1] if group.get('category_id') else ''
                
                if 'sales' in group_name or 'sale' in category:
                    permissions['sales'] = ['read', 'write', 'create', 'delete']
                elif 'hr' in group_name or 'human' in category:
                    permissions['hr'] = ['read', 'write', 'create', 'delete']
                elif 'account' in group_name or 'accounting' in category:
                    permissions['accounting'] = ['read', 'write', 'create', 'delete']
                elif 'inventory' in group_name or 'stock' in category:
                    permissions['inventory'] = ['read', 'write', 'create', 'delete']
                elif 'manufacturing' in group_name or 'mrp' in category:
                    permissions['manufacturing'] = ['read', 'write', 'create', 'delete']
                elif 'purchase' in group_name or 'procurement' in category:
                    permissions['purchasing'] = ['read', 'write', 'create', 'delete']
                elif 'admin' in group_name or 'system' in category:
                    # Admin gets all permissions
                    permissions = {
                        'sales': ['read', 'write', 'create', 'delete'],
                        'hr': ['read', 'write', 'create', 'delete'],
                        'accounting': ['read', 'write', 'create', 'delete'],
                        'inventory': ['read', 'write', 'create', 'delete'],
                        'manufacturing': ['read', 'write', 'create', 'delete'],
                        'purchasing': ['read', 'write', 'create', 'delete'],
                    }
                    break
            
            return permissions
            
        except Exception as e:
            logger.error(f"Error getting permissions: {e}")
            return {}


class LogoutView(APIView):
    """Authentication endpoint for user logout"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # In a real implementation, you might want to blacklist the token
            # For now, we'll just return success
            return Response({
                'success': True,
                'message': 'Successfully logged out'
            })
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshTokenView(APIView):
    """Authentication endpoint for token refresh"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get current user payload
            user_payload = getattr(request, 'user_payload', {})
            if not user_payload:
                return Response({
                    'error': 'Invalid token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate new token with same payload
            token_manager = TokenManager(settings.JWT_SECRET_KEY)
            new_token = token_manager.generate_token(
                client_id=user_payload.get('client_id'),
                user_id=user_payload.get('user_id'),
                permissions=user_payload.get('permissions', {}),
                expires_hours=settings.JWT_EXPIRATION_HOURS
            )
            
            return Response({
                'success': True,
                'token': new_token,
                'expires_in': settings.JWT_EXPIRATION_HOURS * 3600
            })
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserInfoView(APIView):
    """Authentication endpoint for getting current user info"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user_payload = getattr(request, 'user_payload', {})
            if not user_payload:
                return Response({
                    'error': 'Invalid token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({
                'success': True,
                'user': {
                    'id': user_payload.get('user_id'),
                    'database': user_payload.get('client_id'),
                    'permissions': user_payload.get('permissions', {}),
                    'exp': user_payload.get('exp')
                }
            })
            
        except Exception as e:
            logger.error(f"User info error: {e}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateTokenView(APIView):
    """Authentication endpoint for token validation"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            token = request.data.get('token')
            if not token:
                return Response({
                    'error': 'Token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token_manager = TokenManager(settings.JWT_SECRET_KEY)
            payload = token_manager.validate_token(token)
            
            if payload:
                return Response({
                    'success': True,
                    'valid': True,
                    'user': {
                        'id': payload.get('user_id'),
                        'database': payload.get('client_id'),
                        'permissions': payload.get('permissions', {})
                    }
                })
            else:
                return Response({
                    'success': True,
                    'valid': False
                })
                
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 