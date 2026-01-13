from sqlalchemy.orm import Session
from app.models.plan import Plan
from typing import Optional


class PlanDAL:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, plan_id: int) -> Optional[Plan]:
        return self.db.query(Plan).filter(Plan.id == plan_id).first()

    def get_by_name(self, name: str) -> Optional[Plan]:
        return self.db.query(Plan).filter(Plan.name == name).first()

    def get_all(self) -> list[Plan]:
        return self.db.query(Plan).all()

    def create(self, name: str, max_operations: int, price: int, description: str = None) -> Plan:
        plan = Plan(
            name=name,
            max_operations=max_operations,
            price=price,
            description=description
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def update(self, plan: Plan) -> Plan:
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def delete(self, plan: Plan) -> None:
        self.db.delete(plan)
        self.db.commit()
