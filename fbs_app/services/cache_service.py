"""
FBS App Cache Service

Service for managing caching and performance optimization.
"""

import json
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('fbs_app')


class CacheService:
    """Service for managing application caching"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.fbs_config = getattr(settings, 'FBS_APP', {})
        self.cache_enabled = self.fbs_config.get('CACHE_ENABLED', True)
        self.default_timeout = self.fbs_config.get('CACHE_TIMEOUT', 300)  # 5 minutes
        self.redis_url = self.fbs_config.get('REDIS_URL', 'redis://localhost:6379/0')
    
    def get(self, key: str, default=None):
        """Get a value from cache"""
        if not self.cache_enabled:
            return default
        
        try:
            # Scope cache key to this solution
            solution_key = f"{self.solution_name}:{key}"
            value = cache.get(solution_key)
            if value is not None:
                logger.debug(f"Cache hit for solution {self.solution_name}, key: {key}")
            else:
                logger.debug(f"Cache miss for solution {self.solution_name}, key: {key}")
            return value
        except Exception as e:
            logger.warning(f"Cache get error for solution {self.solution_name}, key {key}: {str(e)}")
            return default
    
    def set(self, key: str, value, timeout: int = None):
        """Set a value in cache"""
        if not self.cache_enabled:
            return False
        
        try:
            timeout = timeout or self.default_timeout
            # Scope cache key to this solution
            solution_key = f"{self.solution_name}:{key}"
            cache.set(solution_key, value, timeout)
            logger.debug(f"Cache set for solution {self.solution_name}, key: {key} with timeout: {timeout}s")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for solution {self.solution_name}, key {key}: {str(e)}")
            return False
    
    def delete(self, key: str):
        """Delete a value from cache"""
        if not self.cache_enabled:
            return False
        
        try:
            # Scope cache key to this solution
            solution_key = f"{self.solution_name}:{key}"
            cache.delete(solution_key)
            logger.debug(f"Cache delete for solution {self.solution_name}, key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for solution {self.solution_name}, key {key}: {str(e)}")
            return False
    
    def get_or_set(self, key: str, default_func, timeout: int = None):
        """Get a value from cache or set it using a function if not found"""
        if not self.cache_enabled:
            return default_func()
        
        try:
            # Scope cache key to this solution
            solution_key = f"{self.solution_name}:{key}"
            value = cache.get(solution_key)
            if value is not None:
                logger.debug(f"Cache hit for solution {self.solution_name}, key: {key}")
                return value
            
            # Value not in cache, compute it
            logger.debug(f"Cache miss for solution {self.solution_name}, key: {key}, computing value")
            value = default_func()
            
            # Store in cache
            timeout = timeout or self.default_timeout
            cache.set(solution_key, value, timeout)
            logger.debug(f"Cache set for solution {self.solution_name}, key: {key} with timeout: {timeout}s")
            
            return value
            
        except Exception as e:
            logger.warning(f"Cache get_or_set error for solution {self.solution_name}, key {key}: {str(e)}")
            return default_func()
    
    def get_many(self, keys: list):
        """Get multiple values from cache"""
        if not self.cache_enabled:
            return {key: None for key in keys}
        
        try:
            values = cache.get_many(keys)
            logger.debug(f"Cache get_many for {len(keys)} keys, found {len(values)}")
            return values
        except Exception as e:
            logger.warning(f"Cache get_many error: {str(e)}")
            return {key: None for key in keys}
    
    def set_many(self, data: dict, timeout: int = None):
        """Set multiple values in cache"""
        if not self.cache_enabled:
            return False
        
        try:
            timeout = timeout or self.default_timeout
            cache.set_many(data, timeout)
            logger.debug(f"Cache set_many for {len(data)} keys with timeout: {timeout}s")
            return True
        except Exception as e:
            logger.warning(f"Cache set_many error: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str):
        """Clear cache keys matching a pattern (Redis only)"""
        if not self.cache_enabled:
            return False
        
        try:
            # This is Redis-specific functionality
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
                logger.debug(f"Cache clear pattern: {pattern}")
                return True
            else:
                logger.warning("Pattern-based cache clearing not supported")
                return False
        except Exception as e:
            logger.warning(f"Cache clear pattern error: {str(e)}")
            return False
    
    def increment(self, key: str, delta: int = 1):
        """Increment a numeric value in cache"""
        if not self.cache_enabled:
            return None
        
        try:
            value = cache.incr(key, delta)
            logger.debug(f"Cache increment for key: {key}, delta: {delta}, result: {value}")
            return value
        except Exception as e:
            logger.warning(f"Cache increment error for key {key}: {str(e)}")
            return None
    
    def decrement(self, key: str, delta: int = 1):
        """Decrement a numeric value in cache"""
        if not self.cache_enabled:
            return None
        
        try:
            value = cache.decr(key, delta)
            logger.debug(f"Cache decrement for key: {key}, delta: {delta}, result: {value}")
            return value
        except Exception as e:
            logger.warning(f"Cache decrement error for key {key}: {str(e)}")
            return None
    
    def touch(self, key: str, timeout: int = None):
        """Touch a cache key to extend its timeout"""
        if not self.cache_enabled:
            return False
        
        try:
            timeout = timeout or self.default_timeout
            cache.touch(key, timeout)
            logger.debug(f"Cache touch for key: {key} with timeout: {timeout}s")
            return True
        except Exception as e:
            logger.warning(f"Cache touch error for key {key}: {str(e)}")
            return False
    
    def get_cache_info(self):
        """Get cache statistics and information"""
        if not self.cache_enabled:
            return {
                'enabled': False,
                'message': 'Caching is disabled'
            }
        
        try:
            # Basic cache info
            info = {
                'enabled': True,
                'default_timeout': self.default_timeout,
                'redis_url': self.redis_url,
                'cache_backend': str(type(cache)),
            }
            
            # Try to get Redis info if available
            try:
                if hasattr(cache, 'client') and hasattr(cache.client, 'info'):
                    redis_info = cache.client.info()
                    info['redis_info'] = {
                        'version': redis_info.get('redis_version'),
                        'used_memory': redis_info.get('used_memory_human'),
                        'connected_clients': redis_info.get('connected_clients'),
                        'total_commands_processed': redis_info.get('total_commands_processed'),
                    }
            except Exception:
                pass
            
            return info
            
        except Exception as e:
            logger.warning(f"Error getting cache info: {str(e)}")
            return {
                'enabled': True,
                'error': str(e),
                'message': 'Failed to get cache information'
            }
    
    def clear_all(self):
        """Clear all cache (use with caution)"""
        if not self.cache_enabled:
            return False
        
        try:
            cache.clear()
            logger.warning("Cache cleared completely")
            return True
        except Exception as e:
            logger.error(f"Cache clear all error: {str(e)}")
            return False
    
    def set_with_tags(self, key: str, value, tags: list, timeout: int = None):
        """Set a value with tags for easier management (Redis only)"""
        if not self.cache_enabled:
            return False
        
        try:
            timeout = timeout or self.default_timeout
            
            # Store the value
            cache.set(key, value, timeout)
            
            # Store tags for this key
            tag_key = f"tags:{key}"
            cache.set(tag_key, tags, timeout)
            
            # Store key under each tag
            for tag in tags:
                tag_keys_key = f"tag_keys:{tag}"
                tag_keys = cache.get(tag_keys_key) or []
                if key not in tag_keys:
                    tag_keys.append(key)
                    cache.set(tag_keys_key, tag_keys, timeout)
            
            logger.debug(f"Cache set with tags for key: {key}, tags: {tags}")
            return True
            
        except Exception as e:
            logger.warning(f"Cache set with tags error for key {key}: {str(e)}")
            return False
    
    def clear_by_tag(self, tag: str):
        """Clear all cache keys with a specific tag"""
        if not self.cache_enabled:
            return False
        
        try:
            tag_keys_key = f"tag_keys:{tag}"
            tag_keys = cache.get(tag_keys_key) or []
            
            # Delete all keys with this tag
            for key in tag_keys:
                cache.delete(key)
                cache.delete(f"tags:{key}")
            
            # Delete the tag keys list
            cache.delete(tag_keys_key)
            
            logger.debug(f"Cache cleared by tag: {tag}, affected keys: {len(tag_keys)}")
            return True
            
        except Exception as e:
            logger.warning(f"Cache clear by tag error: {str(e)}")
            return False
