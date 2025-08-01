from django.core.cache import cache
from django.utils import timezone
from ..models import CacheEntry, OdooDatabase
from typing import Any, Optional, Dict
import json
import logging

logger = logging.getLogger('fayvad_core')


class CacheService:
    """Service for caching frequently accessed data"""
    
    DEFAULT_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def get(key: str, database_name: str = None) -> Optional[Any]:
        """Get value from cache"""
        try:
            # First try Redis cache
            value = cache.get(key)
            if value is not None:
                logger.debug(f"Cache hit (Redis): {key}")
                return value
            
            # Then try database cache
            cache_entry = CacheEntry.objects.filter(key=key).first()
            if cache_entry and not cache_entry.is_expired():
                # Update Redis cache
                cache.set(key, cache_entry.value, timeout=CacheService.DEFAULT_TIMEOUT)
                logger.debug(f"Cache hit (DB): {key}")
                return cache_entry.value
            
            logger.debug(f"Cache miss: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, timeout: int = None, database_name: str = None) -> bool:
        """Set value in cache"""
        try:
            timeout = timeout or CacheService.DEFAULT_TIMEOUT
            
            # Set in Redis cache
            cache.set(key, value, timeout=timeout)
            
            # Set in database cache
            database = None
            if database_name:
                try:
                    database = OdooDatabase.objects.get(name=database_name, active=True)
                except OdooDatabase.DoesNotExist:
                    pass
            
            expires_at = timezone.now() + timezone.timedelta(seconds=timeout)
            
            CacheEntry.objects.update_or_create(
                key=key,
                defaults={
                    'value': value,
                    'database': database,
                    'expires_at': expires_at
                }
            )
            
            logger.debug(f"Cache set: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete value from cache"""
        try:
            # Delete from Redis
            cache.delete(key)
            
            # Delete from database
            CacheEntry.objects.filter(key=key).delete()
            
            logger.debug(f"Cache delete: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    @staticmethod
    def clear_database_cache(database_name: str) -> int:
        """Clear all cache entries for a specific database"""
        try:
            database = OdooDatabase.objects.get(name=database_name, active=True)
            
            # Get all cache keys for this database
            cache_entries = CacheEntry.objects.filter(database=database)
            keys = list(cache_entries.values_list('key', flat=True))
            
            # Delete from Redis
            for key in keys:
                cache.delete(key)
            
            # Delete from database
            count = cache_entries.count()
            cache_entries.delete()
            
            logger.info(f"Cleared {count} cache entries for database {database_name}")
            return count
            
        except OdooDatabase.DoesNotExist:
            logger.error(f"Database {database_name} not found")
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache for database {database_name}: {str(e)}")
            return 0
    
    @staticmethod
    def cleanup_expired_cache():
        """Clean up expired cache entries (run this as a scheduled task)"""
        try:
            expired_entries = CacheEntry.objects.filter(expires_at__lt=timezone.now())
            count = expired_entries.count()
            expired_entries.delete()
            
            logger.info(f"Cleaned up {count} expired cache entries")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired cache entries: {str(e)}")
            return 0
    
    @staticmethod
    def get_cache_stats(database_name: str = None) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            stats = {
                'total_entries': CacheEntry.objects.count(),
                'expired_entries': CacheEntry.objects.filter(expires_at__lt=timezone.now()).count(),
                'active_entries': CacheEntry.objects.filter(expires_at__gt=timezone.now()).count()
            }
            
            if database_name:
                try:
                    database = OdooDatabase.objects.get(name=database_name, active=True)
                    stats['database_entries'] = CacheEntry.objects.filter(database=database).count()
                    stats['database_active_entries'] = CacheEntry.objects.filter(
                        database=database, 
                        expires_at__gt=timezone.now()
                    ).count()
                except OdooDatabase.DoesNotExist:
                    pass
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}
    
    @staticmethod
    def cache_model_data(model_name: str, data: Any, database_name: str, timeout: int = None) -> bool:
        """Cache model data with standardized key"""
        key = f"model_data:{database_name}:{model_name}"
        return CacheService.set(key, data, timeout, database_name)
    
    @staticmethod
    def get_cached_model_data(model_name: str, database_name: str) -> Optional[Any]:
        """Get cached model data"""
        key = f"model_data:{database_name}:{model_name}"
        return CacheService.get(key, database_name)
    
    @staticmethod
    def cache_user_data(user_id: int, data: Any, database_name: str, timeout: int = None) -> bool:
        """Cache user-specific data"""
        key = f"user_data:{database_name}:{user_id}"
        return CacheService.set(key, data, timeout, database_name)
    
    @staticmethod
    def get_cached_user_data(user_id: int, database_name: str) -> Optional[Any]:
        """Get cached user data"""
        key = f"user_data:{database_name}:{user_id}"
        return CacheService.get(key, database_name)
