from sqlalchemy.orm import Session
from app.dal.subscription_dal import SubscriptionDAL
from app.dal.plan_dal import PlanDAL
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.config.logging_config import get_logger
from app.utils.cache import cache_service
from app.config.settings import settings

logger = get_logger("subscription_service")


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.subscription_dal = SubscriptionDAL(db)
        self.plan_dal = PlanDAL(db)

    def get_user_active_subscription(self, user_id: int, use_cache: bool = True) -> SubscriptionResponse:
        cache_key = f"subscription:active:user:{user_id}"
        
        if use_cache:
            cached = cache_service.get(cache_key)
            if cached:
                logger.debug(f"Returning cached active subscription for user {user_id}")
                return SubscriptionResponse(**cached)
        
        subscription = self.subscription_dal.get_active_by_user_id(user_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        response = self._to_response(subscription)
        
        if use_cache:
            cache_service.set(cache_key, response.model_dump(), ttl=settings.CACHE_TTL_SUBSCRIPTION)
            logger.debug(f"Cached active subscription for user {user_id}")
        
        return response

    def get_user_subscription_history(self, user_id: int):
        subscriptions = self.subscription_dal.get_all_by_user_id(user_id)
        return [self._to_response(sub) for sub in subscriptions]

    def create_subscription(self, user_id: int, subscription_data: SubscriptionCreate):
        plan = self.plan_dal.get_by_id(subscription_data.plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        
        self.subscription_dal.deactivate_user_subscriptions(user_id)
        
        subscription = self.subscription_dal.create(user_id=user_id, plan_id=plan.id)
        return self._to_response(subscription)

    def upgrade_subscription(self, user_id: int, new_plan_id: int):
        logger.info(f"Upgrading subscription for user {user_id} to plan {new_plan_id}")
        plan = self.plan_dal.get_by_id(new_plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        
        current_subscription = self.subscription_dal.get_active_by_user_id(user_id)
        if not current_subscription:
            logger.info(f"Creating first subscription for user {user_id}")
            return self.create_subscription(user_id, SubscriptionCreate(plan_id=new_plan_id))
        
        if current_subscription.plan_id == new_plan_id:
            logger.info(f"User {user_id} refreshing current plan {new_plan_id} (resetting operation count)")
            now = datetime.now()
            current_subscription.operations_used = 0
            current_subscription.start_date = now
            current_subscription.end_date = now + timedelta(days=30)
            self.subscription_dal.update(current_subscription)
            self._invalidate_subscription_cache(user_id)
            return self._to_response(current_subscription)
        
        current_subscription.is_active = False
        current_subscription.end_date = datetime.now()
        self.subscription_dal.update(current_subscription)
        
        new_subscription = self.subscription_dal.create(user_id=user_id, plan_id=new_plan_id)
        self._invalidate_subscription_cache(user_id)
        logger.info(f"Subscription upgraded: user {user_id} from plan {current_subscription.plan_id} to {new_plan_id}")
        return self._to_response(new_subscription)

    def check_operations_available(self, user_id: int) -> bool:
        subscription = self.subscription_dal.get_active_by_user_id(user_id)
        if not subscription:
            logger.warning(f"Operation check failed - no active subscription for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active subscription"
            )
        
        if not self.subscription_dal.has_operations_remaining(subscription):
            logger.warning(f"Operation limit reached for user {user_id} on plan {subscription.plan.name}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation limit reached for current plan"
            )
        
        return True

    def increment_operation_count(self, user_id: int):
        subscription = self.subscription_dal.get_active_by_user_id(user_id)
        if subscription:
            self.subscription_dal.increment_operations(subscription)
            self._invalidate_subscription_cache(user_id)
    
    def _invalidate_subscription_cache(self, user_id: int):
        cache_service.delete(f"subscription:active:user:{user_id}")
        cache_service.delete(f"subscription:history:user:{user_id}")
        cache_service.delete(f"user:with_subscription:{user_id}")
        logger.debug(f"Subscription cache invalidated for user {user_id}")

    def _to_response(self, subscription) -> SubscriptionResponse:
        return SubscriptionResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            plan_id=subscription.plan_id,
            operations_used=subscription.operations_used,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            is_active=subscription.is_active,
            plan_name=subscription.plan.name,
            max_operations=subscription.plan.max_operations,
            operations_remaining=subscription.plan.max_operations - subscription.operations_used
        )
