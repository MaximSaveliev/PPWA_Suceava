from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PlanBase(BaseModel):
    name: str
    max_operations: int = Field(gt=0, le=2147483647, description="Maximum operations allowed (1 to 2,147,483,647)")
    price: int = Field(ge=0, le=2147483647, description="Price in cents (0 to 2,147,483,647)")
    description: Optional[str] = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    max_operations: Optional[int] = Field(None, gt=0, le=2147483647, description="Maximum operations allowed (1 to 2,147,483,647)")
    price: Optional[int] = Field(None, ge=0, le=2147483647, description="Price in cents (0 to 2,147,483,647)")
    description: Optional[str] = None


class PlanResponse(PlanBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
