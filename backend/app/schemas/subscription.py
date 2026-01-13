from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SubscriptionBase(BaseModel):
    user_id: int
    plan_id: int


class SubscriptionCreate(BaseModel):
    plan_id: int


class SubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    operations_used: Optional[int] = None


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    operations_used: int
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    plan_name: Optional[str] = None
    max_operations: Optional[int] = None
    operations_remaining: Optional[int] = None

    class Config:
        from_attributes = True
