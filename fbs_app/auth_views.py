"""
FBS App Authentication Views

Views for token management and authentication operations.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
import logging

from .services.auth_service import AuthService
from .models import OdooDatabase

logger = logging.getLogger('fbs_app')


@csrf_exempt
@require_http_methods(["POST"])
def create_token(request):
    """Create a new token mapping for a user and database"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['username', 'database_name', 'odoo_token']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)
        
        # Sanitize and validate input
        username = data.get('username', '').strip()
        database_name = data.get('database_name', '').strip()
        odoo_token = data.get('odoo_token', '').strip()
        odoo_user_id = data.get('odoo_user_id')
        
        # Additional validation
        if len(username) < 1 or len(username) > 150:
            return JsonResponse({
                'success': False,
                'error': 'Username must be between 1 and 150 characters'
            }, status=400)
        
        if len(database_name) < 1 or len(database_name) > 100:
            return JsonResponse({
                'success': False,
                'error': 'Database name must be between 1 and 100 characters'
            }, status=400)
        
        if len(odoo_token) < 1:
            return JsonResponse({
                'success': False,
                'error': 'Odoo token cannot be empty'
            }, status=400)
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'User {username} not found'
            }, status=404)
        
        # Create token mapping
        auth_service = AuthService()
        result = auth_service.create_token_mapping(
            user=user,
            database_name=database_name,
            odoo_token=odoo_token,
            odoo_user_id=odoo_user_id
        )
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating token: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validate_token(request):
    """Validate a token mapping"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        database_name = data.get('database_name')
        
        if not all([username, database_name]):
            return JsonResponse({
                'success': False,
                'error': 'Username and database_name are required'
            }, status=400)
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'User {username} not found'
            }, status=404)
        
        # Validate token mapping
        auth_service = AuthService()
        result = auth_service.validate_token_mapping(
            user=user,
            database_name=database_name
        )
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def revoke_token(request):
    """Revoke a token mapping"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        database_name = data.get('database_name')
        
        if not all([username, database_name]):
            return JsonResponse({
                'success': False,
                'error': 'Username and database_name are required'
            }, status=400)
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'User {username} not found'
            }, status=404)
        
        # Revoke token mapping
        auth_service = AuthService()
        result = auth_service.revoke_token_mapping(
            user=user,
            database_name=database_name
        )
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error revoking token: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def list_tokens(request):
    """List all token mappings for a user"""
    try:
        username = request.GET.get('username')
        
        if not username:
            return JsonResponse({
                'success': False,
                'error': 'Username is required'
            }, status=400)
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'User {username} not found'
            }, status=404)
        
        # List token mappings
        auth_service = AuthService()
        result = auth_service.list_token_mappings(user=user)
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except Exception as e:
        logger.error(f"Error listing tokens: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_handshake(request):
    """Create a new handshake for authentication"""
    try:
        data = json.loads(request.body)
        solution_name = data.get('solution_name')
        secret_key = data.get('secret_key')  # Optional, will be generated if not provided
        
        if not solution_name:
            return JsonResponse({
                'success': False,
                'error': 'Solution name is required'
            }, status=400)
        
        # Create handshake
        auth_service = AuthService()
        result = auth_service.create_handshake(
            solution_name=solution_name,
            secret_key=secret_key
        )
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating handshake: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def list_handshakes(request):
    """List all active handshakes"""
    try:
        # Get solution name from query params if provided
        solution_name = request.GET.get('solution_name')
        
        # List handshakes
        auth_service = AuthService()
        result = auth_service.get_active_handshakes(solution_name=solution_name)
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except Exception as e:
        logger.error(f"Error listing handshakes: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validate_handshake(request):
    """Validate a handshake"""
    try:
        data = json.loads(request.body)
        handshake_id = data.get('handshake_id')
        secret_key = data.get('secret_key')
        
        if not all([handshake_id, secret_key]):
            return JsonResponse({
                'success': False,
                'error': 'Handshake ID and secret key are required'
            }, status=400)
        
        # Validate handshake
        auth_service = AuthService()
        result = auth_service.validate_handshake(
            handshake_id=handshake_id,
            secret_key=secret_key
        )
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error validating handshake: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def revoke_handshake(request):
    """Revoke a handshake"""
    try:
        data = json.loads(request.body)
        handshake_id = data.get('handshake_id')
        
        if not handshake_id:
            return JsonResponse({
                'success': False,
                'error': 'Handshake ID is required'
            }, status=400)
        
        # Revoke handshake
        auth_service = AuthService()
        result = auth_service.revoke_handshake(handshake_id=handshake_id)
        
        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error revoking handshake: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
