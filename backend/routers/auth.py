"""
Authentication router for user registration and login.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    decode_access_token,
    security
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Registration failed for existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")
    
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    logger.info(f"User '{current_user.email}' accessed /me endpoint.")
    return UserResponse.model_validate(current_user)


@router.get("/tokens", response_model=dict)
async def get_current_tokens(current_user: User = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current JWT tokens information."""
    # Decode the current access token
    try:
        payload = decode_access_token(credentials.credentials)
        
        # Create token information response
        token_info = {
            "access_token": credentials.credentials,
            "token_type": "bearer",
            "user_id": current_user.id,
            "user_email": current_user.email,
            "token_payload": payload,
            "expires_at": datetime.fromtimestamp(payload.get("exp")) if payload.get("exp") else None,
            "issued_at": datetime.fromtimestamp(payload.get("iat")) if payload.get("iat") else None,
            "token_length": len(credentials.credentials)
        }
        
        logger.info(f"User '{current_user.email}' accessed /tokens endpoint.")
        return token_info
    except Exception as e:
        logger.error(f"Error decoding token for user '{current_user.email}': {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode token"
        )
