"""
Document router for file uploads and text extraction.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User
from models.document import Document, DocumentText
from models.profile import Profile
from schemas.document import DocumentResponse, DocumentTextResponse
from services.llm_service import llm_service
from services.auth_services import get_current_user
from utils.file_utils import (
    validate_file,
    save_upload_file,
    extract_text_from_file
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document. 
    If the document is a resume, it extracts profile information and updates the user's profile.
    """
    print("uploaded file is : ", file)
    print("document type is : ", doc_type)
    print("current user is : ", current_user)

    validate_file(file)
    
    file_path, file_size = await save_upload_file(file, current_user.id)
    
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        doc_type=doc_type
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    try:
        extracted_text, method = extract_text_from_file(file_path)
        
        document_text = DocumentText(
            document_id=document.id,
            extracted_text=extracted_text,
            extraction_method=method
        )
        db.add(document_text)
        db.commit()

        if doc_type == 'resume' and extracted_text:
            # Use LLM to extract profile data
            profile_data = await llm_service.extract_profile_from_text(extracted_text)
            print("extracted profile data: ", profile_data)
            # Check if a profile exists for the user
            user_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
            print("existing user profile: ", user_profile)

            if user_profile:
                # Update existing profile (ignore full_text from LLM)
                update_data = profile_data.dict(
                    exclude_unset=True,
                    exclude={"full_text"}
                )
                print("update data for profile: ", update_data)
                for key, value in update_data.items():
                    setattr(user_profile, key, value)
                # Always use our extracted_text, not whatever the LLM might say
                user_profile.document_id = document.id
                user_profile.full_text = extracted_text
            else:
                # Create new profile, ignore full_text from LLM data
                base_data = profile_data.dict(
                    exclude_unset=True,
                    exclude={"full_text"}
                )
                user_profile = Profile(
                    **base_data,
                    user_id=current_user.id,
                    document_id=document.id,
                    full_text=extracted_text,  # always from our extraction
                )
                db.add(user_profile)
            
            db.commit()

    except Exception as e:
        # In a production environment, you'd want to log this error more robustly.
        # For now, we'll just print it to the console but not fail the whole upload.
        print(f"Error during post-upload processing: {str(e)}")

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
