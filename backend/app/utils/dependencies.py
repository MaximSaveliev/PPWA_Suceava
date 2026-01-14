from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dal.user_dal import UserDAL
from app.utils.security import decode_access_token
from app.schemas.auth import TokenData
from app.config.logging_config import get_logger

logger = get_logger("auth_middleware")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Token validation failed: invalid token")
        raise credentials_exception
    
    user_id: int = payload.get("user_id")
    username: str = payload.get("username")
    role: str = payload.get("role")
    
    if user_id is None or username is None:
        logger.warning("Token validation failed: missing user data")
        raise credentials_exception
    
    user_dal = UserDAL(db)
    user = user_dal.get_by_id(user_id)
    
    if user is None:
        logger.warning(f"Token validation failed: user not found (ID: {user_id})")
        raise credentials_exception
    
    if not user.is_active:
        logger.warning(f"Access denied: inactive user {username} (ID: {user_id})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def get_current_admin_user(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        logger.warning(f"Admin access denied for user: {current_user.username} (ID: {current_user.id})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
    return current_user
