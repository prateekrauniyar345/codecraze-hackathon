"""
Document router for file uploads and text extraction.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User
from models.document import Document, DocumentText, DocumentType
from schemas.document import DocumentResponse, DocumentTextResponse
from utils.auth import get_current_user
from utils.file_utils import (
    validate_file,
    save_upload_file,
    extract_text_from_file
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Query("resume"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document (resume/CV)."""

    print("file received:", file.filename, "of type", doc_type)
    print("current user is : ", current_user.email)
    
    # Validate file
    validate_file(file)
    
    # Save file
    file_path, file_size = await save_upload_file(file, current_user.id)
    print("\n\nfile_path", file_path)
    print("\n\nfile_size", file_size)
    
    print("====================1")
    # Create document record
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        doc_type=doc_type  # Use the string directly, not the enum
    )
    print("====================2")
    
    db.add(document)
    print("====================3")
    db.commit()
    print("====================4")
    db.refresh(document)
    print("====================5")
    
    # Extract text in background (for now, do it synchronously)
    try:
        extracted_text, method = extract_text_from_file(file_path)
        print("\n\nextracted_text", extracted_text)
        print("\n\nmethod", method)
        
        document_text = DocumentText(
            document_id=document.id,
            extracted_text=extracted_text,
            extraction_method=method
        )
        
        db.add(document_text)
        db.commit()
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Text extraction failed: {str(e)}")
    
    return DocumentResponse.from_orm(document)


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for current user."""
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.uploaded_at.desc()).all()
    
    return [DocumentResponse.from_orm(doc) for doc in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentResponse.from_orm(document)


@router.get("/{document_id}/text", response_model=DocumentTextResponse)
async def get_document_text(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get extracted text from a document."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document_text = db.query(DocumentText).filter(
        DocumentText.document_id == document_id
    ).first()
    
    if not document_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Text not extracted yet"
        )
    
    return DocumentTextResponse.from_orm(document_text)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db.delete(document)
    db.commit()
    
    return None
