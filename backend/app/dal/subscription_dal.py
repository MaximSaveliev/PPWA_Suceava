from sqlalchemy.orm import Session, joinedload
from app.models.subscription import Subscription
from app.models.plan import Plan
from typing import Optional
from datetime import datetime, timedelta


class SubscriptionDAL:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        return self.db.query(Subscription).options(joinedload(Subscription.plan)).filter(
            Subscription.id == subscription_id
        ).first()

    def get_active_by_user_id(self, user_id: int) -> Optional[Subscription]:
        return self.db.query(Subscription).options(joinedload(Subscription.plan)).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()

    def get_all_by_user_id(self, user_id: int) -> list[Subscription]:
        return self.db.query(Subscription).options(joinedload(Subscription.plan)).filter(
            Subscription.user_id == user_id
        ).order_by(Subscription.start_date.desc()).all()

    def create(self, user_id: int, plan_id: int) -> Subscription:
        now = datetime.now()
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            operations_used=0,
            start_date=now,
            end_date=now + timedelta(days=30)
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def update(self, subscription: Subscription) -> Subscription:
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def increment_operations(self, subscription: Subscription) -> Subscription:
        subscription.operations_used += 1
        return self.update(subscription)

    def deactivate_user_subscriptions(self, user_id: int) -> None:
        self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).update({"is_active": False, "end_date": datetime.now()})
        self.db.commit()

    def has_operations_remaining(self, subscription: Subscription) -> bool:
        return subscription.operations_used < subscription.plan.max_operations
