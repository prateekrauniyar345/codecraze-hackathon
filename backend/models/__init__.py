"""
SQLAlchemy models for ScholarSense application.
"""
from .user import User
from .document import Document, DocumentText, DocumentType
from .profile import Profile
from .opportunity import Opportunity, OpportunityRequirement, OpportunityStatus
from .material import GeneratedMaterial, MaterialType

__all__ = [
    "User",
    "Document",
    "DocumentText",
    "DocumentType",
    "Profile",
    "Opportunity",
    "OpportunityRequirement",
    "OpportunityStatus",
    "GeneratedMaterial",
    "MaterialType",
]
