"""
Opportunity schemas for tracking applications.
"""
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from models.opportunity import OpportunityStatus, OpportunityType


class OpportunityCreate(BaseModel):
    """Schema for creating an opportunity."""
    title: str = Field(..., max_length=512)
    organization: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = None
    description: str
    deadline: Optional[date] = None
    type: Optional[OpportunityType] = None


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""
    title: Optional[str] = Field(None, max_length=512)
    organization: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[OpportunityStatus] = None
    type: Optional[OpportunityType] = None
    deadline: Optional[date] = None


class RequirementResponse(BaseModel):
    """Schema for opportunity requirement response."""
    id: int
    requirement_text: str
    requirement_type: Optional[str] = None
    is_mandatory: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OpportunityResponse(BaseModel):
    """Schema for opportunity response."""
    id: int
    user_id: int
    title: str
    organization: Optional[str] = None
    url: Optional[str] = None
    description: str
    fit_score: Optional[int] = None
    fit_analysis: Optional[Dict[str, Any]] = None
    status: OpportunityStatus
    type: OpportunityType
    deadline: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    requirements: List[RequirementResponse] = []
    
    class Config:
        from_attributes = True


class OpportunityAnalysisRequest(BaseModel):
    """Schema for requesting opportunity analysis."""
    opportunity_text: str = Field(..., description="The full text of the opportunity (job posting, scholarship, etc.)")
    profile_id: Optional[int] = Field(None, description="Specific profile ID to use for analysis")


class OpportunityAnalysisResponse(BaseModel):
    """Schema for opportunity analysis response."""
    fit_score: int = Field(..., ge=0, le=100, description="Overall fit score (0-100)")
    fit_analysis: Dict[str, Any] = Field(..., description="Detailed fit analysis")
    extracted_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="Parsed requirements")
