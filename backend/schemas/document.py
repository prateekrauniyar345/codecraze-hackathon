"""
Document schemas for file uploads and text extraction.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models.document import DocumentType


class DocumentUpload(BaseModel):
    """Schema for document upload metadata."""
    doc_type: DocumentType = DocumentType.RESUME


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: int
    user_id: int
    filename: str
    file_path: str
    file_size: Optional[int] = None
    doc_type: DocumentType
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class DocumentTextResponse(BaseModel):
    """Schema for extracted document text."""
    id: int
    document_id: int
    extracted_text: str
    extraction_method: str
    extracted_at: datetime
    
    class Config:
        from_attributes = True
