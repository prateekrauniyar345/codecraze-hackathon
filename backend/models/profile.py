"""
Profile model for user's structured resume data.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Profile(Base):
    """User profile model with structured resume data."""
    
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    full_text = Column(Text, nullable=False)
    skills = Column(JSONB, default=list)
    education = Column(JSONB, default=list)
    experience = Column(JSONB, default=list)
    projects = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profiles")
    document = relationship("Document", back_populates="profiles")
    
    def __repr__(self):
        return f"<Profile(id={self.id}, user_id={self.user_id})>"
