"""
FBS FastAPI Cache Service

PRESERVED from Django cache_service.py - managing caching and performance optimization.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from .service_interfaces import BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class CacheService(BaseService, AsyncServiceMixin):
    """Service for managing application caching - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        # Load from FastAPI config
        from ..core.config import config
        self.cache_enabled = getattr(config, 'cache_enabled', True)
        self.default_timeout = 300  # 5 minutes
        self.redis_url = getattr(config, 'redis_url', None)
        self._memory_cache = {}  # Simple in-memory cache for now

    async def get(self, key: str, default=None) -> Any:
        """Get a value from cache - PRESERVED from Django"""
        if not self.cache_enabled:
            return default

        try:
            # Scope cache key to this solution
            solution_key = f"{self.solution_name}:{key}"

            # Try Redis first if available, fallback to in-memory
            if self.redis_url:
                try:
                    import redis
                    redis_client = redis.from_url(self.redis_url)
                    cached_value = redis_client.get(solution_key)
                    if cached_value:
                        logger.debug(f"Redis cache hit for solution {self.solution_name}, key: {key}")
                        return cached_value.decode('utf-8') if isinstance(cached_value, bytes) else cached_value
                except Exception as e:
                    logger.warning(f"Redis cache error: {e}, falling back to memory cache")

            # Check in-memory cache
            if solution_key in self._memory_cache:
                value, expiry = self._memory_cache[solution_key]
                if expiry is None or datetime.now() < expiry:
                    logger.debug(f"Memory cache hit for solution {self.solution_name}, key: {key}")
                    return value
                else:
                    # Expired, remove from cache
                    del self._memory_cache[solution_key]

            logger.debug(f"Cache miss for solution {self.solution_name}, key: {key}")
            return default

        except Exception as e:
            logger.warning(f"Cache get error for solution {self.solution_name}, key {key}: {str(e)}")
            return default

    async def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set a value in cache - PRESERVED from Django"""
        if not self.cache_enabled:
            return False

        try:
            timeout = timeout or self.default_timeout
            # Scope cache key to this solution
            solution_key = f"{self.solution_name}:{key}"

            # Calculate expiry time
            expiry = datetime.now() + timedelta(seconds=timeout) if timeout else None

            # Store in Redis if available, otherwise memory cache
            if self.redis_url:
                try:
                    import redis
                    redis_client = redis.from_url(self.redis_url)
                    redis_client.setex(solution_key, timeout, str(value))
                    logger.debug(f"Redis cache set for solution {self.solution_name}, key: {key}")
                except Exception as e:
                    logger.warning(f"Redis cache error: {e}, falling back to memory cache")
                    self._memory_cache[solution_key] = (value, expiry)
            else:
                self._memory_cache[solution_key] = (value, expiry)

            logger.debug(f"Cache set for solution {self.solution_name}, key: {key} with timeout: {timeout}s")
            return True

        except Exception as e:
            logger.warning(f"Cache set error for solution {self.solution_name}, key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a value from cache - PRESERVED from Django"""
        if not self.cache_enabled:
            return False

        try:
            solution_key = f"{self.solution_name}:{key}"

            if solution_key in self._memory_cache:
                del self._memory_cache[solution_key]
                logger.debug(f"Cache delete for solution {self.solution_name}, key: {key}")
                return True

            return False

        except Exception as e:
            logger.warning(f"Cache delete error for solution {self.solution_name}, key {key}: {str(e)}")
            return False

    async def has_key(self, key: str) -> bool:
        """Check if key exists in cache - PRESERVED from Django"""
        if not self.cache_enabled:
            return False

        try:
            solution_key = f"{self.solution_name}:{key}"

            if solution_key not in self._memory_cache:
                return False

            value, expiry = self._memory_cache[solution_key]
            if expiry is None or datetime.now() < expiry:
                return True
            else:
                # Expired, remove from cache
                del self._memory_cache[solution_key]
                return False

        except Exception as e:
            logger.warning(f"Cache has_key error for solution {self.solution_name}, key {key}: {str(e)}")
            return False

    async def incr(self, key: str, delta: int = 1) -> Optional[int]:
        """Increment a numeric value in cache - PRESERVED from Django"""
        if not self.cache_enabled:
            return None

        try:
            solution_key = f"{self.solution_name}:{key}"

            if solution_key in self._memory_cache:
                value, expiry = self._memory_cache[solution_key]
                if isinstance(value, (int, float)):
                    new_value = value + delta
                    self._memory_cache[solution_key] = (new_value, expiry)
                    return new_value

            return None

        except Exception as e:
            logger.warning(f"Cache incr error for solution {self.solution_name}, key {key}: {str(e)}")
            return None

    async def decr(self, key: str, delta: int = 1) -> Optional[int]:
        """Decrement a numeric value in cache - PRESERVED from Django"""
        return await self.incr(key, -delta)

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache - PRESERVED from Django"""
        if not self.cache_enabled:
            return {}

        try:
            result = {}
            for key in keys:
                value = await self.get(key)
                if value is not None:
                    result[key] = value

            logger.debug(f"Cache get_many for solution {self.solution_name}, keys: {keys}, found: {len(result)}")
            return result

        except Exception as e:
            logger.warning(f"Cache get_many error for solution {self.solution_name}: {str(e)}")
            return {}

    async def set_many(self, data: Dict[str, Any], timeout: Optional[int] = None) -> bool:
        """Set multiple values in cache - PRESERVED from Django"""
        if not self.cache_enabled:
            return False

        try:
            success = True
            for key, value in data.items():
                if not await self.set(key, value, timeout):
                    success = False

            logger.debug(f"Cache set_many for solution {self.solution_name}, keys: {list(data.keys())}, success: {success}")
            return success

        except Exception as e:
            logger.warning(f"Cache set_many error for solution {self.solution_name}: {str(e)}")
            return False

    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple values from cache - PRESERVED from Django"""
        if not self.cache_enabled:
            return 0

        try:
            deleted_count = 0
            for key in keys:
                if await self.delete(key):
                    deleted_count += 1

            logger.debug(f"Cache delete_many for solution {self.solution_name}, keys: {keys}, deleted: {deleted_count}")
            return deleted_count

        except Exception as e:
            logger.warning(f"Cache delete_many error for solution {self.solution_name}: {str(e)}")
            return 0

    async def clear(self) -> bool:
        """Clear all cache entries for this solution - PRESERVED from Django"""
        if not self.cache_enabled:
            return False

        try:
            # Remove all keys for this solution
            keys_to_delete = [key for key in self._memory_cache.keys() if key.startswith(f"{self.solution_name}:")]

            for key in keys_to_delete:
                del self._memory_cache[key]

            logger.debug(f"Cache clear for solution {self.solution_name}, deleted: {len(keys_to_delete)} keys")
            return True

        except Exception as e:
            logger.warning(f"Cache clear error for solution {self.solution_name}: {str(e)}")
            return False

    async def get_or_set(self, key: str, default: Any, timeout: Optional[int] = None) -> Any:
        """Get a value from cache, or set it if it doesn't exist - PRESERVED from Django"""
        value = await self.get(key)
        if value is None:
            if callable(default):
                value = default()
            else:
                value = default
            await self.set(key, value, timeout)

        return value

    async def touch(self, key: str, timeout: Optional[int] = None) -> bool:
        """Update the expiry time for a cache key - PRESERVED from Django"""
        if not self.cache_enabled:
            return False

        try:
            solution_key = f"{self.solution_name}:{key}"

            if solution_key in self._memory_cache:
                value, _ = self._memory_cache[solution_key]
                expiry = datetime.now() + timedelta(seconds=timeout) if timeout else None
                self._memory_cache[solution_key] = (value, expiry)
                logger.debug(f"Cache touch for solution {self.solution_name}, key: {key}, timeout: {timeout}")
                return True

            return False

        except Exception as e:
            logger.warning(f"Cache touch error for solution {self.solution_name}, key {key}: {str(e)}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics - PRESERVED from Django"""
        try:
            solution_keys = [key for key in self._memory_cache.keys() if key.startswith(f"{self.solution_name}:")]
            total_keys = len(solution_keys)

            # Count expired keys
            expired_keys = 0
            now = datetime.now()
            for key in solution_keys:
                value, expiry = self._memory_cache[key]
                if expiry and now >= expiry:
                    expired_keys += 1

            active_keys = total_keys - expired_keys

            return {
                'solution_name': self.solution_name,
                'total_keys': total_keys,
                'active_keys': active_keys,
                'expired_keys': expired_keys,
                'cache_enabled': self.cache_enabled,
                'default_timeout': self.default_timeout
            }

        except Exception as e:
            logger.warning(f"Cache stats error for solution {self.solution_name}: {str(e)}")
            return {
                'solution_name': self.solution_name,
                'error': str(e)
            }

    async def cleanup_expired(self) -> int:
        """Remove expired cache entries - PRESERVED from Django"""
        try:
            expired_keys = []
            now = datetime.now()

            for key, (value, expiry) in self._memory_cache.items():
                if expiry and now >= expiry:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._memory_cache[key]

            logger.debug(f"Cache cleanup for solution {self.solution_name}, removed: {len(expired_keys)} expired keys")
            return len(expired_keys)

        except Exception as e:
            logger.warning(f"Cache cleanup error for solution {self.solution_name}: {str(e)}")
            return 0

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            stats = await self.get_cache_stats()
            return {
                'service': 'cache',
                'status': 'healthy' if self.cache_enabled else 'disabled',
                'cache_enabled': self.cache_enabled,
                'total_keys': stats.get('total_keys', 0),
                'active_keys': stats.get('active_keys', 0),
                'default_timeout': self.default_timeout,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'service': 'cache',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
