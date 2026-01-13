from sqlalchemy.orm import Session
from app.dal.user_dal import UserDAL
from app.schemas.user import UserCreate, UserUpdate, UserWithSubscription
from app.dal.subscription_dal import SubscriptionDAL
from app.dal.plan_dal import PlanDAL
from app.utils.security import hash_password
from fastapi import HTTPException, status
from typing import Optional


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_dal = UserDAL(db)
        self.subscription_dal = SubscriptionDAL(db)
        self.plan_dal = PlanDAL(db)

    def get_user_by_id(self, user_id: int):
        user = self.user_dal.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def get_user_with_subscription(self, user_id: int) -> UserWithSubscription:
        user = self.get_user_by_id(user_id)
        subscription = self.subscription_dal.get_active_by_user_id(user_id)
        
        user_data = UserWithSubscription(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        if subscription:
            user_data.current_plan = subscription.plan.name
            user_data.operations_used = subscription.operations_used
            user_data.operations_remaining = subscription.plan.max_operations - subscription.operations_used
        
        return user_data

    def get_all_users(self, skip: int = 0, limit: int = 100):
        return self.user_dal.get_all(skip, limit)
    
    def get_all_users_with_subscription(self, skip: int = 0, limit: int = 100):
        users = self.user_dal.get_all(skip, limit)
        result = []
        
        for user in users:
            subscription = self.subscription_dal.get_active_by_user_id(user.id)
            
            user_data = UserWithSubscription(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at
            )
            
            if subscription:
                user_data.current_plan = subscription.plan.name
                user_data.operations_used = subscription.operations_used
                user_data.operations_remaining = subscription.plan.max_operations - subscription.operations_used
            
            result.append(user_data)
        
        return result

    def create_user(self, user_data: UserCreate):
        if self.user_dal.get_by_email(user_data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        if self.user_dal.get_by_username(user_data.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        
        hashed_pwd = hash_password(user_data.password)
        user = self.user_dal.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_pwd,
            role="user"
        )
        
        free_plan = self.plan_dal.get_by_name("FREE")
        if free_plan:
            self.subscription_dal.create(user_id=user.id, plan_id=free_plan.id)
        
        return user

    def update_user(self, user_id: int, user_data: UserUpdate):
        user = self.get_user_by_id(user_id)
        
        if user_data.email and user_data.email != user.email:
            if self.user_dal.get_by_email(user_data.email):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
            user.email = user_data.email
        
        if user_data.username and user_data.username != user.username:
            if self.user_dal.get_by_username(user_data.username):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
            user.username = user_data.username
        
        if user_data.password:
            user.hashed_password = hash_password(user_data.password)
        
        if user_data.role is not None:
            user.role = user_data.role
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        return self.user_dal.update(user)

    def delete_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        self.user_dal.delete(user)

    def deactivate_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        return self.user_dal.deactivate(user)
