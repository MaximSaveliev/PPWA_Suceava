from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.plan_service import PlanService
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
    use_cache: bool = True,
    db: Session = Depends(get_db)
):
    plan_service = PlanService(db)
    return plan_service.get_all_plans(include_deleted=include_deleted, use_cache=use_cache)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: int,
    use_cache: bool = True,
    db: Session = Depends(get_db)
):
    plan_service = PlanService(db)
    plan = plan_service.get_plan_by_id(plan_id, include_deleted=False, use_cache=use_cache)
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
    plan_service = PlanService(db)
    
    existing = plan_service.get_plan_by_name(plan_data.name, include_deleted=True, use_cache=False)
    if existing:
        logger.warning(f"Plan creation failed - name already exists: {plan_data.name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan with this name already exists"
        )
    
    return plan_service.create_plan(plan_data)
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.username} updating plan {plan_id}")
    plan_service = PlanService(db)
    plan = plan_service.get_plan_by_id(plan_id, include_deleted=False, use_cache=False)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    if plan_data.name and plan_data.name != plan.name:
        existing = plan_service.get_plan_by_name(plan_data.name, include_deleted=True, use_cache=False)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan with this name already exists"
            )
    
    return plan_service.update_plan(plan_id, plan_data)


@router.delete("/{plan_id}/soft", response_model=PlanResponse)
def soft_delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.username} soft deleting plan {plan_id}")
    plan_service = PlanService(db)
    plan = plan_service.get_plan_by_id(plan_id, include_deleted=False, use_cache=False)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    return plan_service.soft_delete_plan(plan_id)


@router.post("/{plan_id}/restore", response_model=PlanResponse)
def restore_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.username} restoring plan {plan_id}")
    plan_service = PlanService(db)
    plan = plan_service.get_plan_by_id(plan_id, include_deleted=True, use_cache=False)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    if not plan.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan is not deleted"
        )
    
    return plan_service.restore_plan(plan_id)


@router.delete("/{plan_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    logger.warning(f"Admin {current_user.username} hard deleting plan {plan_id}")
    plan_service = PlanService(db)
    plan = plan_service.get_plan_by_id(plan_id, include_deleted=True, use_cache=False)
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    try:
        plan_service.hard_delete_plan(plan_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete plan. It may be referenced by existing subscriptions."
        )
