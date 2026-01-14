# Cache Implementation Documentation

## Overview

The application implements a Redis-based caching mechanism at the Service layer to improve performance for frequently accessed data.

## Architecture

### Cache Service
- **Location**: `app/utils/cache.py`
- **Type**: Redis-based with fallback (disabled if Redis unavailable)
- **Features**:
  - Get/Set operations with TTL
  - Pattern-based deletion
  - JSON serialization
  - Automatic error handling

### Configuration
- **File**: `app/config/settings.py`
- **Settings**:
  - `REDIS_HOST`: Redis server host (default: localhost)
  - `REDIS_PORT`: Redis server port (default: 6379)
  - `REDIS_DB`: Redis database number (default: 0)
  - `CACHE_TTL_PLANS`: Plans cache TTL (default: 600s)
  - `CACHE_TTL_USER`: User cache TTL (default: 300s)
  - `CACHE_TTL_SUBSCRIPTION`: Subscription cache TTL (default: 300s)

## Cached Entities

### 1. Plans
**Service**: `PlanService`
**Cache Keys**:
- `plans:all:deleted_{bool}` - All plans list
- `plan:id:{plan_id}` - Individual plan by ID
- `plan:name:{name}` - Individual plan by name

**Operations with Caching**:
- `get_all_plans(use_cache=True)` - Returns all plans
- `get_plan_by_id(plan_id, use_cache=True)` - Returns plan by ID
- `get_plan_by_name(name, use_cache=True)` - Returns plan by name

**Cache Invalidation**: Triggered on create, update, soft delete, restore, hard delete

### 2. Subscriptions
**Service**: `SubscriptionService`
**Cache Keys**:
- `subscription:active:user:{user_id}` - Active subscription for user

**Operations with Caching**:
- `get_user_active_subscription(user_id, use_cache=True)` - Returns active subscription

**Cache Invalidation**: Triggered on upgrade, operation count increment

### 3. Users
**Service**: `UserService`
**Cache Keys**:
- `user:id:{user_id}` - User by ID
- `user:with_subscription:{user_id}` - User with subscription details

**Operations with Caching**:
- `get_user_by_id(user_id, use_cache=True)` - Returns user by ID
- `get_user_with_subscription(user_id, use_cache=True)` - Returns user with subscription

**Cache Invalidation**: Triggered on update, delete, deactivate

## API Usage

### Enabling/Disabling Cache

All endpoints that support caching have an optional `use_cache` query parameter:

```http
GET /api/v1/plans?use_cache=true
GET /api/v1/plans/{id}?use_cache=false
GET /api/v1/subscriptions/my-subscription?use_cache=true
```

**Default**: `use_cache=true` (caching enabled)

### Examples

#### Get plans with cache
```bash
curl http://localhost:8000/api/v1/plans
```

#### Get plans without cache (force database query)
```bash
curl http://localhost:8000/api/v1/plans?use_cache=false
```

#### Get specific plan with cache
```bash
curl http://localhost:8000/api/v1/plans/1?use_cache=true
```

## Cache Invalidation Strategy

### Automatic Invalidation
Cache is automatically invalidated when:
1. **Plans**: Create, update, delete, restore operations
2. **Subscriptions**: Upgrade, operation count changes
3. **Users**: Update, delete, deactivate operations

### Cross-Entity Invalidation
When invalidating user cache, related subscription cache is also cleared to maintain consistency.

## Implementation Details

### Service Layer Pattern

```python
def get_entity(self, entity_id: int, use_cache: bool = True):
    cache_key = f"entity:id:{entity_id}"
    
    if use_cache:
        cached = cache_service.get(cache_key)
        if cached:
            logger.debug(f"Cache hit: {cache_key}")
            return cached
    
    entity = self.dal.get_by_id(entity_id)
    
    if use_cache and entity:
        cache_service.set(cache_key, entity_dict, ttl=TTL)
        logger.debug(f"Cache set: {cache_key}")
    
    return entity

def update_entity(self, entity_id: int, data):
    entity = self.dal.update(entity_id, data)
    self._invalidate_cache(entity_id)
    return entity

def _invalidate_cache(self, entity_id: int):
    cache_service.delete(f"entity:id:{entity_id}")
    cache_service.delete_pattern("entity:list:*")
```

## Performance Considerations

### Cache Hit Benefits
- **Plans**: 600s TTL - reduces DB queries for frequently accessed pricing data
- **Users**: 300s TTL - improves authentication and profile access speed
- **Subscriptions**: 300s TTL - faster subscription checks during image processing

### Cache Miss Handling
- Graceful fallback to database
- Automatic cache population on miss
- No impact on functionality if Redis unavailable

## Monitoring

### Logging
All cache operations are logged at DEBUG level:
- Cache hits
- Cache misses
- Cache sets
- Cache invalidations

### Example Logs
```
DEBUG - app.cache - Cache hit: plan:id:1
DEBUG - app.plan_service - Returning cached plan 1
INFO - app.plan_service - Plan updated and cache invalidated: 1
DEBUG - app.cache - Cache pattern delete: plans:* (3 keys)
```

## Deployment Notes

### Redis Installation
```bash
# Windows (using Chocolatey)
choco install redis-64

# Linux (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Without Redis
If Redis is not available, the cache service automatically disables itself and all operations fall back to database queries. No code changes required.

## Best Practices

1. **Use cache for read operations**: GET endpoints should use caching
2. **Disable cache for writes**: Create/Update/Delete should use `use_cache=False` when checking existing data
3. **Invalidate related caches**: When updating one entity affects another, invalidate both
4. **Monitor cache hit ratio**: Use Redis INFO stats to track cache effectiveness
5. **Adjust TTL based on data volatility**: Longer TTL for rarely changing data (plans), shorter for frequently updated data (subscriptions)
