from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dal.plan_dal import PlanDAL
from app.schemas.plan import PlanResponse, PlanCreate, PlanUpdate
from app.utils.dependencies import get_current_admin_user
from app.models.user import User
from typing import List

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get("/", response_model=List[PlanResponse])
def get_all_plans(
    include_deleted: bool = False,
    db: Session = Depends(get_db)
):
    plan_dal = PlanDAL(db)
    return plan_dal.get_all(include_deleted=include_deleted)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    plan_dal = PlanDAL(db)
    plan = plan_dal.get_by_id(plan_id, include_deleted=False)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_data: PlanCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    plan_dal = PlanDAL(db)
    
    # Check if plan with same name exists (including deleted ones)
    existing = plan_dal.get_by_name(plan_data.name, include_deleted=True)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan with this name already exists"
        )
    
    return plan_dal.create(
        name=plan_data.name,
        max_operations=plan_data.max_operations,
        price=plan_data.price,
        description=plan_data.description
    )


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    plan_dal = PlanDAL(db)
    plan = plan_dal.get_by_id(plan_id, include_deleted=False)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    if plan_data.name and plan_data.name != plan.name:
        existing = plan_dal.get_by_name(plan_data.name, include_deleted=True)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan with this name already exists"
            )
        plan.name = plan_data.name
    
    if plan_data.max_operations is not None:
        plan.max_operations = plan_data.max_operations
    
    if plan_data.price is not None:
        plan.price = plan_data.price
    
    if plan_data.description is not None:
        plan.description = plan_data.description
    
    return plan_dal.update(plan)


@router.delete("/{plan_id}/soft", response_model=PlanResponse)
def soft_delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    plan_dal = PlanDAL(db)
    plan = plan_dal.get_by_id(plan_id, include_deleted=False)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    return plan_dal.soft_delete(plan)


@router.post("/{plan_id}/restore", response_model=PlanResponse)
def restore_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    plan_dal = PlanDAL(db)
    plan = plan_dal.get_by_id(plan_id, include_deleted=True)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    if not plan.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan is not deleted"
        )
    
    return plan_dal.restore(plan)


@router.delete("/{plan_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    plan_dal = PlanDAL(db)
    plan = plan_dal.get_by_id(plan_id, include_deleted=True)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    try:
        plan_dal.hard_delete(plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete plan. It may be referenced by existing subscriptions."
        )
