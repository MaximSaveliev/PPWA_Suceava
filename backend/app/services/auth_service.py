from sqlalchemy.orm import Session
from app.dal.user_dal import UserDAL
from app.utils.security import verify_password, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger("auth_service")


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_dal = UserDAL(db)

    def authenticate_user(self, username: str, password: str):
        logger.info(f"Authentication attempt for: {username}")
        user = self.user_dal.get_by_username(username)
        if not user:
            user = self.user_dal.get_by_email(username)
        
        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed authentication for: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning(f"Inactive account login attempt: {username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        logger.info(f"User authenticated successfully: {user.username} (ID: {user.id})")
        return user

    def create_token(self, user):
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_id": user.id, "username": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        logger.info(f"Token generated for user: {user.username} (ID: {user.id})")
        return {"access_token": access_token, "token_type": "bearer"}
