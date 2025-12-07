"""
Opportunity models for jobs, internships, scholarships, etc.
"""
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Date, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum
from database import Base


class OpportunityStatus(str, enum.Enum):
    """Opportunity status enumeration."""
    TO_APPLY = "TO_APPLY"
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"


class Opportunity(Base):
    """Opportunity model for tracking applications."""
    
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(512), nullable=False)
    organization = Column(String(255))
    url = Column(Text)
    description = Column(Text, nullable=False)
    fit_score = Column(Integer, CheckConstraint('fit_score >= 0 AND fit_score <= 100'))
    fit_analysis = Column(JSONB)
    status = Column(Enum(OpportunityStatus), default=OpportunityStatus.TO_APPLY)
    deadline = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="opportunities")
    requirements = relationship("OpportunityRequirement", back_populates="opportunity", cascade="all, delete-orphan")
    generated_materials = relationship("GeneratedMaterial", back_populates="opportunity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, title='{self.title}')>"


class OpportunityRequirement(Base):
    """Requirements parsed from opportunity descriptions."""
    
    __tablename__ = "opportunity_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    requirement_text = Column(Text, nullable=False)
    requirement_type = Column(String(100))
    is_mandatory = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="requirements")
    
    def __repr__(self):
        return f"<OpportunityRequirement(id={self.id}, opportunity_id={self.opportunity_id})>"
