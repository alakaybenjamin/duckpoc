from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime, timedelta

from database import get_db
from models.database_models import User
from models.schemas import UserCreate, UserLogin, Token
from services.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

def get_user_by_email(db: Session, email: str):
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.error(f"Database error while fetching user by email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    try:
        logger.info(f"Login attempt for user: {form_data.username}")

        user = get_user_by_email(db, form_data.username)  # username field contains email
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"Successful login for user: {form_data.username}")
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred during login"
        )

@router.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        logger.info(f"Attempting to register new user with email: {user.email}")

        db_user = get_user_by_email(db, user.email)
        if db_user:
            logger.warning(f"Registration attempt with existing email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"Successfully registered user with email: {user.email}")

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred during registration"
        )