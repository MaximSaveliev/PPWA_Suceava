from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.subscription_service import SubscriptionService
from app.services.plan_service import PlanService
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.schemas.plan import PlanResponse
from app.utils.dependencies import get_current_user
from app.models.user import User
from typing import List

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=List[PlanResponse])
def get_all_plans(use_cache: bool = True, db: Session = Depends(get_db)):
    plan_service = PlanService(db)
    return plan_service.get_all_plans(include_deleted=False, use_cache=use_cache)


@router.get("/my-subscription", response_model=SubscriptionResponse)
def get_my_subscription(
    use_cache: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.get_user_active_subscription(current_user.id, use_cache=use_cache)


@router.get("/history", response_model=List[SubscriptionResponse])
def get_subscription_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.get_user_subscription_history(current_user.id)


@router.post("/upgrade", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def upgrade_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.upgrade_subscription(current_user.id, subscription_data.plan_id)
