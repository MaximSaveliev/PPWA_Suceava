import redis
from typing import Optional, Any
import json
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger("cache")

class CacheService:
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                decode_responses=True
            )
            self.redis_client.ping()
            self.enabled = True
            logger.info("Cache service initialized successfully")
        except (redis.ConnectionError, AttributeError) as e:
            logger.warning(f"Redis not available, caching disabled: {str(e)}")
            self.redis_client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str):
        if not self.enabled:
            return False
        
        try:
            result = self.redis_client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def delete_pattern(self, pattern: str):
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info(f"Cache pattern delete: {pattern} ({result} keys)")
                return result
            return 0
        except Exception as e:
            logger.error(f"Cache pattern delete error for {pattern}: {str(e)}")
            return 0
    
    def clear_all(self):
        if not self.enabled:
            return False
        
        try:
            self.redis_client.flushdb()
            logger.info("Cache cleared completely")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False

cache_service = CacheService()
