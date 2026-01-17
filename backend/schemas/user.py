"""
User schemas for authentication and user management.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class User(BaseModel):
    '''
    id : int primary key for the user table
    oauth_id : str unique identifier from the OAuth provider
    oauth_provider : str name of the OAuth provider (e.g., 'google', 'auth0')
    full_name : Optional[str] full name of the user
    email : EmailStr email address of the user
    created_at : datetime timestamp when the user was created
    last_login : datetime timestamp of the user's last login
    '''
    id: int
    oauth_id: str
    oauth_provider: str
    full_name: Optional[str] = None
    email: EmailStr
    created_at: datetime
    last_login: datetime   


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    oauth_id: str
    oauth_provider: str
    full_name: Optional[str] = None
    email: EmailStr 


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None    


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    oauth_id: str
    oauth_provider: str
    full_name: Optional[str] = None
    email: EmailStr
    created_at: datetime
    last_login: datetime

    class Config:
        # This is the magic line that fixes your error
        from_attributes = True


