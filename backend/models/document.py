"""
Document models for file uploads and text extraction.
"""
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration."""
    RESUME = "resume"
    CV = "cv"
    OTHER = "other"


class Document(Base):
    """Document model for uploaded files."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer)
    doc_type = Column(Enum(DocumentType), default=DocumentType.RESUME)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
    document_texts = relationship("DocumentText", back_populates="document", cascade="all, delete-orphan")
    profiles = relationship("Profile", back_populates="document")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"


class DocumentText(Base):
    """Extracted text from documents."""
    
    __tablename__ = "document_texts"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    extracted_text = Column(Text, nullable=False)
    extraction_method = Column(String(50), default="pypdf2")
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="document_texts")
    
    def __repr__(self):
        return f"<DocumentText(id={self.id}, document_id={self.document_id})>"
