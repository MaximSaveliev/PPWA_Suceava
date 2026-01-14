from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dal.plan_dal import PlanDAL
from app.schemas.plan import PlanResponse, PlanCreate, PlanUpdate
from app.utils.dependencies import get_current_admin_user
from app.models.user import User
from typing import List
from app.config.logging_config import get_logger

logger = get_logger("plan_controller")

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
    logger.info(f"Admin {current_user.username} creating plan: {plan_data.name}")
    plan_dal = PlanDAL(db)
    
    existing = plan_dal.get_by_name(plan_data.name, include_deleted=True)
    if existing:
        logger.warning(f"Plan creation failed - name already exists: {plan_data.name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan with this name already exists"
        )
    
    plan = plan_dal.create(
        name=plan_data.name,
        max_operations=plan_data.max_operations,
        price=plan_data.price,
        description=plan_data.description
    )
    logger.info(f"Plan created: {plan.name} (ID: {plan.id}, Max ops: {plan.max_operations}, Price: {plan.price})")
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.username} updating plan {plan_id}")
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
    
    result = plan_dal.update(plan)
    logger.info(f"Plan updated: {result.name} (ID: {plan_id})")
    return result


@router.delete("/{plan_id}/soft", response_model=PlanResponse)
def soft_delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.username} soft deleting plan {plan_id}")
    plan_dal = PlanDAL(db)
    plan = plan_dal.get_by_id(plan_id, include_deleted=False)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    result = plan_dal.soft_delete(plan)
    logger.info(f"Plan soft deleted: {result.name} (ID: {plan_id})")
    return result


@router.post("/{plan_id}/restore", response_model=PlanResponse)
def restore_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.username} restoring plan {plan_id}")
    plan_dal = PlanDAL(db)
    plan = plan_dal.get_by_id(plan_id, include_deleted=True)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    if not plan.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan is not deleted"
        )
    
    result = plan_dal.restore(plan)
    logger.info(f"Plan restored: {result.name} (ID: {plan_id})")
    return result


@router.delete("/{plan_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    logger.warning(f"Admin {current_user.username} hard deleting plan {plan_id}")
    plan_dal = PlanDAL(db)
    plan = plan_dal.get_by_id(plan_id, include_deleted=True)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    try:
        plan_dal.hard_delete(plan)
        logger.info(f"Plan hard deleted: {plan.name} (ID: {plan_id})")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete plan. It may be referenced by existing subscriptions."
        )
