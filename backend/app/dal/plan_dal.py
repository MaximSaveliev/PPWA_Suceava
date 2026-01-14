from sqlalchemy.orm import Session
from app.models.plan import Plan
from typing import Optional
from datetime import datetime


class PlanDAL:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, plan_id: int, include_deleted: bool = False) -> Optional[Plan]:
        query = self.db.query(Plan).filter(Plan.id == plan_id)
        if not include_deleted:
            query = query.filter(Plan.is_deleted == False)
        return query.first()

    def get_by_name(self, name: str, include_deleted: bool = False) -> Optional[Plan]:
        query = self.db.query(Plan).filter(Plan.name == name)
        if not include_deleted:
            query = query.filter(Plan.is_deleted == False)
        return query.first()

    def get_all(self, include_deleted: bool = False) -> list[Plan]:
        query = self.db.query(Plan)
        if not include_deleted:
            query = query.filter(Plan.is_deleted == False)
        return query.all()

    def create(self, name: str, max_operations: int, price: int, description: str = None) -> Plan:
        plan = Plan(
            name=name,
            max_operations=max_operations,
            price=price,
            description=description,
            is_deleted=False
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def update(self, plan: Plan) -> Plan:
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def soft_delete(self, plan: Plan) -> Plan:
        plan.is_deleted = True
        plan.deleted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def restore(self, plan: Plan) -> Plan:
        plan.is_deleted = False
        plan.deleted_at = None
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def hard_delete(self, plan: Plan) -> None:
        self.db.delete(plan)
        self.db.commit()
