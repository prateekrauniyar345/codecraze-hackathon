"""
Material schemas for AI-generated content.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models.material import MaterialType


class MaterialGenerateRequest(BaseModel):
    """Schema for requesting material generation."""
    opportunity_id: int
    material_types: list[MaterialType] = Field(..., description="Types of materials to generate")
    profile_id: Optional[int] = Field(None, description="Specific profile to use (defaults to user's latest)")


class MaterialResponse(BaseModel):
    """Schema for generated material response."""
    id: int
    opportunity_id: int
    user_id: int
    material_type: MaterialType
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
