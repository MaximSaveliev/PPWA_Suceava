from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse
from app.config.logging_config import get_logger

logger = get_logger("auth_controller")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registration request for username: {user_data.username}")
    user_service = UserService(db)
    return user_service.create_user(user_data)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login request for: {form_data.username}")
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    return auth_service.create_token(user)
