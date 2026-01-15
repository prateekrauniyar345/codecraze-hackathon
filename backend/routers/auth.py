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
from schemas.user import User, UserCreate, UserResponse, UserUpdate
from services.auth_services import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    decode_access_token,
    security
)
from fastapi.requests import Request
from services.oauth_client import oauth
from services.auth_services import create_access_token
router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

# ----------------------------------------
#  old registration and login endpoints 
# ----------------------------------------
# @router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
# async def register(user_data: UserCreate, db: Session = Depends(get_db)):
#     """Register a new user."""
#     existing_user = db.query(User).filter(User.email == user_data.email).first()
#     if existing_user:
#         logger.warning(f"Registration failed for existing email: {user_data.email}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered"
#         )
    
#     hashed_password = get_password_hash(user_data.password)
#     new_user = User(
#         email=user_data.email,
#         hashed_password=hashed_password,
#         full_name=user_data.full_name
#     )
    
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
    
#     logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")
    
    
#     # Create access token
#     access_token = create_access_token(data={"sub": str(new_user.id)})
    
#     return Token(
#         access_token=access_token,
#         user=UserResponse.model_validate(new_user)
#     )


# @router.post("/login", response_model=Token)
# async def login(credentials: UserLogin, db: Session = Depends(get_db)):
#     """Login user and return JWT token."""
#     user = authenticate_user(db, credentials.email, credentials.password)
    
#     if not user:
#         logger.warning(f"Failed login attempt for email: {credentials.email}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Create access token
#     access_token = create_access_token(data={"sub": str(user.id)})
    
#     logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")
    
#     return Token(
#         access_token=access_token,
#         user=UserResponse.model_validate(user)
#     )


# ----------------------------------------
#  new login and registration endpoints
# ----------------------------------------
@router.get("/login")
async def oauth_login(request: Request):
    """OAuth login placeholder endpoint."""
    logger.info("OAuth login endpoint accessed.")
    redirect_uri = request.url_for("oauth_callback")
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

@router.get("/callback", name="oauth_callback")
async def oauth_callback(request: Request, db=Depends(get_db)):
    """OAuth callback endpoint to handle authentication response."""
    logger.info("OAuth callback endpoint accessed.")
    token = await oauth.auth0.authorize_access_token(request)
    print("OAuth token received:", token)
    # user_info = await oauth.auth0.parse_id_token(request, token)
    user_info = token.get('userinfo')
    print("User info received from Auth0:", user_info)
    
    # Check if user exists in the database
    user = db.query(User).filter(User.email == user_info["email"]).first()
    
    if not user:
        # Create new user if not exists
        user = User(
            email=user_info["email"],
            full_name=user_info.get("name", ""),
            
            
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New OAuth user created: {user.email} (ID: {user.id})")
    else:
        logger.info(f"Existing OAuth user logged in: {user.email} (ID: {user.id})")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }




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
