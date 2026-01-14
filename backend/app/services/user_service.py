from sqlalchemy.orm import Session
from app.dal.user_dal import UserDAL
from app.schemas.user import UserCreate, UserUpdate, UserWithSubscription
from app.dal.subscription_dal import SubscriptionDAL
from app.dal.plan_dal import PlanDAL
from app.utils.security import hash_password
from fastapi import HTTPException, status
from typing import Optional
from app.config.logging_config import get_logger
from app.utils.cache import cache_service
from app.config.settings import settings

logger = get_logger("user_service")


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_dal = UserDAL(db)
        self.subscription_dal = SubscriptionDAL(db)
        self.plan_dal = PlanDAL(db)

    def get_user_by_id(self, user_id: int, use_cache: bool = True):
        cache_key = f"user:id:{user_id}"
        
        if use_cache:
            cached = cache_service.get(cache_key)
            if cached:
                logger.debug(f"Returning cached user {user_id}")
                return self._dict_to_user(cached)
        
        user = self.user_dal.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if use_cache:
            cache_service.set(cache_key, self._user_to_dict(user), ttl=settings.CACHE_TTL_USER)
            logger.debug(f"Cached user {user_id}")
        
        return user

    def get_user_with_subscription(self, user_id: int, use_cache: bool = True) -> UserWithSubscription:
        cache_key = f"user:with_subscription:{user_id}"
        
        if use_cache:
            cached = cache_service.get(cache_key)
            if cached:
                logger.debug(f"Returning cached user with subscription {user_id}")
                return UserWithSubscription(**cached)
        
        user = self.get_user_by_id(user_id, use_cache=use_cache)
        subscription = self.subscription_dal.get_active_by_user_id(user_id)
        
        user_data = UserWithSubscription(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        if subscription:
            user_data.current_plan = subscription.plan.name
            user_data.operations_used = subscription.operations_used
            user_data.operations_remaining = subscription.plan.max_operations - subscription.operations_used
        
        if use_cache:
            cache_service.set(cache_key, user_data.model_dump(), ttl=settings.CACHE_TTL_USER)
            logger.debug(f"Cached user with subscription {user_id}")
        
        return user_data

    def get_all_users(self, skip: int = 0, limit: int = 100):
        return self.user_dal.get_all(skip, limit)
    
    def get_all_users_with_subscription(self, skip: int = 0, limit: int = 100):
        users = self.user_dal.get_all(skip, limit)
        result = []
        
        for user in users:
            subscription = self.subscription_dal.get_active_by_user_id(user.id)
            
            user_data = UserWithSubscription(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at
            )
            
            if subscription:
                user_data.current_plan = subscription.plan.name
                user_data.operations_used = subscription.operations_used
                user_data.operations_remaining = subscription.plan.max_operations - subscription.operations_used
            
            result.append(user_data)
        
        return result

    def create_user(self, user_data: UserCreate):
        logger.info(f"Creating new user: {user_data.username} ({user_data.email})")
        
        if self.user_dal.get_by_email(user_data.email):
            logger.warning(f"User creation failed - email already exists: {user_data.email}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        if self.user_dal.get_by_username(user_data.username):
            logger.warning(f"User creation failed - username already exists: {user_data.username}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        
        hashed_pwd = hash_password(user_data.password)
        user = self.user_dal.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_pwd,
            role="user"
        )
        
        free_plan = self.plan_dal.get_by_name("FREE")
        if free_plan:
            self.subscription_dal.create(user_id=user.id, plan_id=free_plan.id)
            logger.info(f"User created successfully with FREE plan: {user.username} (ID: {user.id})")
        else:
            logger.warning(f"User created without subscription - FREE plan not found: {user.username} (ID: {user.id})")
        
        return user

    def update_user(self, user_id: int, user_data: UserUpdate):
        user = self.get_user_by_id(user_id)
        logger.info(f"Updating user: {user.username} (ID: {user_id})")
        
        if user_data.email and user_data.email != user.email:
            if self.user_dal.get_by_email(user_data.email):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
            user.email = user_data.email
        
        if user_data.username and user_data.username != user.username:
            if self.user_dal.get_by_username(user_data.username):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
            user.username = user_data.username
        
        if user_data.password:
            user.hashed_password = hash_password(user_data.password)
        
        if user_data.role is not None:
            user.role = user_data.role
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        result = self.user_dal.update(user)
        self._invalidate_user_cache(user_id)
        logger.info(f"User updated successfully: {user.username} (ID: {user_id})")
        return result

    def delete_user(self, user_id: int):
        user = self.get_user_by_id(user_id, use_cache=False)
        logger.warning(f"Deleting user: {user.username} (ID: {user_id})")
        self.user_dal.delete(user)
        self._invalidate_user_cache(user_id)
        logger.info(f"User deleted: {user.username} (ID: {user_id})")

    def deactivate_user(self, user_id: int):
        user = self.get_user_by_id(user_id, use_cache=False)
        logger.info(f"Deactivating user: {user.username} (ID: {user_id})")
        result = self.user_dal.deactivate(user)
        self._invalidate_user_cache(user_id)
        logger.info(f"User deactivated: {user.username} (ID: {user_id})")
        return result
    
    def _invalidate_user_cache(self, user_id: int):
        cache_service.delete(f"user:id:{user_id}")
        cache_service.delete(f"user:with_subscription:{user_id}")
        cache_service.delete(f"subscription:active:user:{user_id}")
        logger.debug(f"User cache invalidated for {user_id}")
    
    def _user_to_dict(self, user):
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    
    def _dict_to_user(self, data):
        from app.models.user import User
        from datetime import datetime
        user = User()
        user.id = data["id"]
        user.email = data["email"]
        user.username = data["username"]
        user.role = data["role"]
        user.is_active = data["is_active"]
        user.hashed_password = data["hashed_password"]
        user.created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        return user
