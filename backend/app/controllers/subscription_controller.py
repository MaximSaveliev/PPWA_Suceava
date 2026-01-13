from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.subscription_service import SubscriptionService
from app.dal.plan_dal import PlanDAL
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.schemas.plan import PlanResponse
from app.utils.dependencies import get_current_user
from app.models.user import User
from typing import List

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=List[PlanResponse])
def get_all_plans(db: Session = Depends(get_db)):
    plan_dal = PlanDAL(db)
    return plan_dal.get_all()


@router.get("/my-subscription", response_model=SubscriptionResponse)
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.get_user_active_subscription(current_user.id)


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
