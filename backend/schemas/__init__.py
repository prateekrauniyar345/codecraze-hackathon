"""
Pydantic schemas for request/response validation.
"""
from .user import User, UserCreate, UserUpdate, UserResponse
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

# Grants schemas
from .grants import (
    SortOption,
    PaginationReq,
    OneOfFilter,
    BoolOneOfFilter,
    DateRangeFilter,
    NumberRangeFilter,
    Filters,
    GrantSuggestion,
    GrantSuggestionsResponse,
    GrantsSearchRequest,
    GrantsSearchItem,
    GrantsSearchResponse,
    GrantAPIOpportunity,
    PaginationInfo,
    GrantsAPISearchResponse,
)


__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
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
    # Grants exports
    "SortOption",
    "PaginationReq",
    "OneOfFilter",
    "BoolOneOfFilter",
    "DateRangeFilter",
    "NumberRangeFilter",
    "Filters",
    "GrantSuggestion",
    "GrantSuggestionsResponse",
    "GrantsSearchRequest",
    "GrantsSearchItem",
    "GrantsSearchResponse",
    "GrantAPIOpportunity",
    "PaginationInfo",
    "GrantsAPISearchResponse",
]