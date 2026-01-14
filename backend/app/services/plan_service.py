from sqlalchemy.orm import Session
from app.dal.plan_dal import PlanDAL
from app.schemas.plan import PlanCreate, PlanUpdate
from app.utils.cache import cache_service
from app.config.settings import settings
from app.config.logging_config import get_logger
from typing import List, Optional

logger = get_logger("plan_service")

class PlanService:
    def __init__(self, db: Session):
        self.db = db
        self.plan_dal = PlanDAL(db)
    
    def get_all_plans(self, include_deleted: bool = False, use_cache: bool = True) -> List:
        cache_key = "plans"
        
        if use_cache:
            cached = cache_service.get(cache_key)
            if cached:
                logger.debug("Returning cached plans")
                plans = [self._dict_to_plan(p) for p in cached]
                if not include_deleted:
                    plans = [p for p in plans if not p.is_deleted]
                return plans
        
        plans = self.plan_dal.get_all(include_deleted=True)
        
        if use_cache:
            plans_dict = [self._plan_to_dict(p) for p in plans]
            cache_service.set(cache_key, plans_dict, ttl=settings.CACHE_TTL_PLANS)
            logger.debug("Cached all plans")
        
        if not include_deleted:
            plans = [p for p in plans if not p.is_deleted]
        
        return plans
    
    def get_plan_by_id(self, plan_id: int, include_deleted: bool = False, use_cache: bool = True):
        cache_key = f"plan:id:{plan_id}"
        
        if use_cache:
            cached = cache_service.get(cache_key)
            if cached:
                logger.debug(f"Returning cached plan {plan_id}")
                return self._dict_to_plan(cached)
        
        plan = self.plan_dal.get_by_id(plan_id, include_deleted=include_deleted)
        
        if plan and use_cache:
            cache_service.set(cache_key, self._plan_to_dict(plan), ttl=settings.CACHE_TTL_PLANS)
            logger.debug(f"Cached plan {plan_id}")
        
        return plan
    
    def get_plan_by_name(self, name: str, include_deleted: bool = False, use_cache: bool = True):
        cache_key = f"plan:name:{name}"
        
        if use_cache:
            cached = cache_service.get(cache_key)
            if cached:
                logger.debug(f"Returning cached plan {name}")
                return self._dict_to_plan(cached)
        
        plan = self.plan_dal.get_by_name(name, include_deleted=include_deleted)
        
        if plan and use_cache:
            cache_service.set(cache_key, self._plan_to_dict(plan), ttl=settings.CACHE_TTL_PLANS)
            logger.debug(f"Cached plan {name}")
        
        return plan
    
    def create_plan(self, plan_data: PlanCreate):
        logger.info(f"Creating plan: {plan_data.name}")
        plan = self.plan_dal.create(
            name=plan_data.name,
            max_operations=plan_data.max_operations,
            price=plan_data.price,
            description=plan_data.description
        )
        self._invalidate_plan_cache()
        logger.info(f"Plan created and cache invalidated: {plan.name} (ID: {plan.id})")
        return plan
    
    def update_plan(self, plan_id: int, plan_data: PlanUpdate):
        logger.info(f"Updating plan {plan_id}")
        plan = self.plan_dal.get_by_id(plan_id, include_deleted=False)
        
        if plan_data.name is not None:
            plan.name = plan_data.name
        if plan_data.max_operations is not None:
            plan.max_operations = plan_data.max_operations
        if plan_data.price is not None:
            plan.price = plan_data.price
        if plan_data.description is not None:
            plan.description = plan_data.description
        
        updated_plan = self.plan_dal.update(plan)
        self._invalidate_plan_cache(plan_id)
        logger.info(f"Plan updated and cache invalidated: {plan_id}")
        return updated_plan
    
    def soft_delete_plan(self, plan_id: int):
        logger.info(f"Soft deleting plan {plan_id}")
        plan = self.plan_dal.get_by_id(plan_id, include_deleted=False)
        deleted_plan = self.plan_dal.soft_delete(plan)
        self._invalidate_plan_cache(plan_id)
        logger.info(f"Plan soft deleted and cache invalidated: {plan_id}")
        return deleted_plan
    
    def restore_plan(self, plan_id: int):
        logger.info(f"Restoring plan {plan_id}")
        plan = self.plan_dal.get_by_id(plan_id, include_deleted=True)
        restored_plan = self.plan_dal.restore(plan)
        self._invalidate_plan_cache(plan_id)
        logger.info(f"Plan restored and cache invalidated: {plan_id}")
        return restored_plan
    
    def hard_delete_plan(self, plan_id: int):
        logger.warning(f"Hard deleting plan {plan_id}")
        plan = self.plan_dal.get_by_id(plan_id, include_deleted=True)
        self.plan_dal.hard_delete(plan)
        self._invalidate_plan_cache(plan_id)
        logger.info(f"Plan hard deleted and cache invalidated: {plan_id}")
    
    def _invalidate_plan_cache(self, plan_id: Optional[int] = None):
        cache_service.delete("plans")
        if plan_id:
            cache_service.delete(f"plan:id:{plan_id}")
        cache_service.delete_pattern("plan:name:*")
        logger.debug(f"Plan cache invalidated (plan_id={plan_id})")
    
    def _plan_to_dict(self, plan):
        return {
            "id": plan.id,
            "name": plan.name,
            "max_operations": plan.max_operations,
            "price": plan.price,
            "description": plan.description,
            "is_deleted": plan.is_deleted,
            "deleted_at": plan.deleted_at.isoformat() if plan.deleted_at else None,
            "created_at": plan.created_at.isoformat() if plan.created_at else None
        }
    
    def _dict_to_plan(self, data):
        from app.models.plan import Plan
        from datetime import datetime
        plan = Plan()
        plan.id = data["id"]
        plan.name = data["name"]
        plan.max_operations = data["max_operations"]
        plan.price = data["price"]
        plan.description = data["description"]
        plan.is_deleted = data["is_deleted"]
        plan.deleted_at = datetime.fromisoformat(data["deleted_at"]) if data.get("deleted_at") else None
        plan.created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        return plan
