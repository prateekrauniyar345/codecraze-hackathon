"""
Generated material models for AI-generated application content.
"""
import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class MaterialType(str, enum.Enum):
    """Material type enumeration."""
    EMAIL = "email"
    SUBJECT_LINE = "subject_line"
    SOP_PARAGRAPH = "sop_paragraph"
    FIT_BULLETS = "fit_bullets"


class GeneratedMaterial(Base):
    """AI-generated application materials."""
    
    __tablename__ = "generated_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # material_type = Column(Enum(MaterialType), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships (commented out)
    opportunity = relationship("Opportunity", back_populates="generated_materials")
    user = relationship("User", back_populates="generated_materials")
    
    def __repr__(self):
        return f"<GeneratedMaterial(id={self.id})>"
