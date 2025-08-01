from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from ..models import OdooDatabase, ApiTokenMapping
from .odoo_client import odoo_client, OdooClientError
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger('fayvad_core')


class AuthService:
    """Service for handling authentication and token management"""
    
    @staticmethod
    def get_user_token(user: User, database_name: str) -> Optional[str]:
        """Get Odoo token for user and database"""
        try:
            database = OdooDatabase.objects.get(name=database_name, active=True)
            token_mapping = ApiTokenMapping.objects.get(
                user=user,
                database=database,
                active=True
            )
            
            if token_mapping.is_expired():
                logger.warning(f"Token expired for user {user.username} and database {database_name}")
                return None
            
            # Update last used timestamp
            token_mapping.update_last_used()
            
            return token_mapping.odoo_token
            
        except (OdooDatabase.DoesNotExist, ApiTokenMapping.DoesNotExist):
            logger.error(f"No token mapping found for user {user.username} and database {database_name}")
            return None
    
    @staticmethod
    def create_token_mapping(user: User, database_name: str, odoo_token: str, 
                           odoo_user_id: int, expires_at: timezone.datetime = None) -> ApiTokenMapping:
        """Create or update token mapping for user and database"""
        try:
            database = OdooDatabase.objects.get(name=database_name, active=True)
            
            token_mapping, created = ApiTokenMapping.objects.update_or_create(
                user=user,
                database=database,
                defaults={
                    'odoo_token': odoo_token,
                    'odoo_user_id': odoo_user_id,
                    'expires_at': expires_at,
                    'active': True
                }
            )
            
            action = "Created" if created else "Updated"
            logger.info(f"{action} token mapping for user {user.username} and database {database_name}")
            
            return token_mapping
            
        except OdooDatabase.DoesNotExist:
            logger.error(f"Database {database_name} not found")
            raise ValueError(f"Database {database_name} not found")
    
    @staticmethod
    def validate_database_access(user: User, database_name: str) -> bool:
        """Validate if user has access to database"""
        try:
            database = OdooDatabase.objects.get(name=database_name, active=True)
            token_mapping = ApiTokenMapping.objects.get(
                user=user,
                database=database,
                active=True
            )
            
            return not token_mapping.is_expired()
            
        except (OdooDatabase.DoesNotExist, ApiTokenMapping.DoesNotExist):
            return False
    
    @staticmethod
    def get_user_databases(user: User) -> list:
        """Get list of databases accessible by user"""
        token_mappings = ApiTokenMapping.objects.filter(
            user=user,
            active=True,
            database__active=True
        ).select_related('database')
        
        databases = []
        for mapping in token_mappings:
            if not mapping.is_expired():
                databases.append({
                    'name': mapping.database.name,
                    'display_name': mapping.database.display_name,
                    'description': mapping.database.description
                })
        
        return databases
    
    @staticmethod
    def revoke_token(user: User, database_name: str) -> bool:
        """Revoke token for user and database"""
        try:
            database = OdooDatabase.objects.get(name=database_name, active=True)
            token_mapping = ApiTokenMapping.objects.get(
                user=user,
                database=database
            )
            
            token_mapping.active = False
            token_mapping.save()
            
            logger.info(f"Revoked token for user {user.username} and database {database_name}")
            return True
            
        except (OdooDatabase.DoesNotExist, ApiTokenMapping.DoesNotExist):
            logger.error(f"No token mapping found for user {user.username} and database {database_name}")
            return False
    
    @staticmethod
    def cleanup_expired_tokens():
        """Clean up expired tokens (run this as a scheduled task)"""
        expired_tokens = ApiTokenMapping.objects.filter(
            expires_at__lt=timezone.now(),
            active=True
        )
        
        count = expired_tokens.count()
        expired_tokens.update(active=False)
        
        logger.info(f"Cleaned up {count} expired tokens")
        return count
