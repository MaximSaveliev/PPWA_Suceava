from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlanBase(BaseModel):
    name: str
    max_operations: int
    price: int
    description: Optional[str] = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    max_operations: Optional[int] = None
    price: Optional[int] = None
    description: Optional[str] = None


class PlanResponse(PlanBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
