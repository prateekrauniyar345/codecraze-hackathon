"""
Pydantic schemas for request/response validation.
"""
from .user import UserCreate, UserLogin, UserResponse, Token
from .document import DocumentUpload, DocumentResponse, DocumentTextResponse
from .profile import ProfileCreate, ProfileUpdate, ProfileResponse
from .opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    OpportunityAnalysisRequest,
    OpportunityAnalysisResponse,
    RequirementResponse
)
from .material import (
    MaterialGenerateRequest,
    MaterialResponse,
    MaterialType
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "DocumentUpload",
    "DocumentResponse",
    "DocumentTextResponse",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "OpportunityCreate",
    "OpportunityUpdate",
    "OpportunityResponse",
    "OpportunityAnalysisRequest",
    "OpportunityAnalysisResponse",
    "RequirementResponse",
    "MaterialGenerateRequest",
    "MaterialResponse",
    "MaterialType",
]
