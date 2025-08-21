"""
FBS App Authentication Service

Service for managing handshake authentication and user sessions.
"""

import secrets
import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

logger = logging.getLogger('fbs_app')


class AuthService:
    """Service for managing authentication and handshakes"""
    
    def __init__(self):
        self.fbs_config = getattr(settings, 'FBS_APP', {})
        self.handshake_expiry_hours = self.fbs_config.get('HANDSHAKE_EXPIRY_HOURS', 24)
    
    def create_handshake(self, solution_name: str, secret_key: str = None, expiry_hours: int = None) -> dict:
        """Create a new handshake for system authentication"""
        try:
            from ..models import Handshake
            
            # Generate secure handshake ID and secret key
            handshake_id = secrets.token_urlsafe(32)
            if not secret_key:
                secret_key = secrets.token_urlsafe(32)
            
            # Set expiry time
            expiry_hours = expiry_hours or self.handshake_expiry_hours
            expires_at = timezone.now() + timedelta(hours=expiry_hours)
            
            # Create handshake
            handshake = Handshake.objects.create(
                handshake_id=handshake_id,
                solution_name=solution_name,
                secret_key=secret_key,
                status='pending',
                expires_at=expires_at
            )
            
            logger.info(f"Created handshake for {solution_name}")
            
            return {
                'success': True,
                'data': {
                    'handshake_id': handshake_id,
                    'secret_key': secret_key,
                    'expires_at': expires_at,
                    'id': handshake.id
                },
                'message': 'Handshake created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating handshake: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create handshake'
            }
    
    def validate_handshake(self, handshake_id: str, secret_key: str) -> dict:
        """Validate a handshake ID and secret key"""
        try:
            from ..models import Handshake
            
            # Find handshake
            handshake = Handshake.objects.get(
                handshake_id=handshake_id,
                status='active'
            )
            
            # Validate secret key
            if handshake.secret_key != secret_key:
                return {
                    'success': False,
                    'error': 'Invalid secret key',
                    'message': 'Handshake secret key is invalid'
                }
            
            # Check expiry
            if timezone.now() > handshake.expires_at:
                # Mark as expired
                handshake.status = 'expired'
                handshake.save(update_fields=['status'])
                
                return {
                    'success': False,
                    'error': 'Expired handshake',
                    'message': 'Handshake has expired'
                }
            
            # Update last used
            handshake.last_used = timezone.now()
            handshake.save(update_fields=['last_used'])
            
            return {
                'success': True,
                'data': {
                    'handshake': handshake,
                    'user': handshake.user,
                    'database': handshake.database,
                    'system_name': handshake.system_name,
                    'permissions': handshake.permissions,
                    'expires_at': handshake.expires_at
                },
                'message': 'Handshake validated successfully'
            }
            
        except Handshake.DoesNotExist:
            return {
                'success': False,
                'error': 'Invalid token',
                'message': 'Handshake token not found'
            }
        except Exception as e:
            logger.error(f"Error validating handshake: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to validate handshake'
            }
    
    def revoke_handshake(self, handshake_id: str) -> dict:
        """Revoke a handshake"""
        try:
            from ..models import Handshake
            
            # Find and revoke handshake
            handshake = Handshake.objects.get(handshake_id=handshake_id, status='active')
            handshake.status = 'revoked'
            handshake.save(update_fields=['status'])
            
            logger.info(f"Revoked handshake for {handshake.solution_name}")
            
            return {
                'success': True,
                'message': 'Handshake revoked successfully'
            }
            
        except Handshake.DoesNotExist:
            return {
                'success': False,
                'error': 'Handshake not found',
                'message': 'Handshake not found'
            }
        except Exception as e:
            logger.error(f"Error revoking handshake: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to revoke handshake'
            }
    
    def get_active_handshakes(self, solution_name: str = None) -> dict:
        """Get active handshakes for a solution"""
        try:
            from ..models import Handshake
            
            # Build query
            query = {'status': 'active'}
            if solution_name:
                query['solution_name'] = solution_name
            
            # Get handshakes
            handshakes = Handshake.objects.filter(**query)
            
            # Filter out expired handshakes
            active_handshakes = []
            for handshake in handshakes:
                if timezone.now() <= handshake.expires_at:
                    active_handshakes.append(handshake)
                else:
                    # Mark expired handshakes as expired
                    handshake.status = 'expired'
                    handshake.save(update_fields=['status'])
            
            return {
                'success': True,
                'data': {
                    'handshakes': active_handshakes,
                    'count': len(active_handshakes)
                },
                'message': f'Found {len(active_handshakes)} active handshakes'
            }
            
        except Exception as e:
            logger.error(f"Error getting active handshakes: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get active handshakes'
            }
    
    def cleanup_expired_handshakes(self) -> dict:
        """Clean up expired handshakes"""
        try:
            from ..models import Handshake
            
            # Find expired handshakes
            expired_handshakes = Handshake.objects.filter(
                status='active',
                expires_at__lt=timezone.now()
            )
            
            count = expired_handshakes.count()
            
            # Mark expired handshakes as expired
            expired_handshakes.update(status='expired')
            
            logger.info(f"Cleaned up {count} expired handshakes")
            
            return {
                'success': True,
                'data': {'cleaned_count': count},
                'message': f'Cleaned up {count} expired handshakes'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired handshakes: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to clean up expired handshakes'
            }
    
    def create_token_mapping(self, user: User, database_name: str, 
                           odoo_token: str, odoo_user_id: int,
                           expiry_hours: int = None) -> dict:
        """Create token mapping for Odoo integration"""
        try:
            from ..models import TokenMapping, OdooDatabase
            
            # Get or create database
            database, created = OdooDatabase.objects.get_or_create(
                name=database_name,
                defaults={
                    'display_name': database_name.replace('_', ' ').title(),
                    'odoo_db_name': database_name,
                    'base_url': self.fbs_config.get('ODOO_BASE_URL', 'http://localhost:8069'),
                    'active': True
                }
            )
            
            # Set expiry time
            expiry_hours = expiry_hours or self.handshake_expiry_hours
            expires_at = timezone.now() + timedelta(hours=expiry_hours) if expiry_hours > 0 else None
            
            # Create token mapping
            token_mapping = TokenMapping.objects.create(
                user=user,
                database=database,
                odoo_token=odoo_token,
                odoo_user_id=odoo_user_id,
                expires_at=expires_at,
                active=True
            )
            
            logger.info(f"Created token mapping for {user.username} -> {database_name}")
            
            return {
                'success': True,
                'data': {
                    'token_mapping_id': token_mapping.id,
                    'expires_at': expires_at
                },
                'message': 'Token mapping created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating token mapping: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create token mapping'
            }
