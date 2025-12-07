"""
Profile schemas for user profile data.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class ProfileCreate(BaseModel):
    """Schema for creating a profile."""
    document_id: Optional[int] = None
    full_text: str
    skills: List[str] = []
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []


class ProfileUpdate(BaseModel):
    """Schema for updating a profile."""
    full_text: Optional[str] = None
    skills: Optional[List[str]] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None


class ProfileResponse(BaseModel):
    """Schema for profile response."""
    id: int
    user_id: int
    document_id: Optional[int] = None
    full_text: str
    skills: List[str]
    education: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
