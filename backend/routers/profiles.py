"""
Profile router for managing user profiles.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User
from models.profile import Profile
from models.document import DocumentText
from schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from services.auth_services import get_current_user

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new profile."""
    profile = Profile(
        user_id=current_user.id,
        document_id=profile_data.document_id,
        full_text=profile_data.full_text,
        skills=profile_data.skills,
        education=profile_data.education,
        experience=profile_data.experience,
        projects=profile_data.projects
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return ProfileResponse.from_orm(profile)


@router.post("/from-document/{document_id}", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile_from_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a profile from a document's extracted text."""
    # Get document text
    document_text = db.query(DocumentText).join(
        DocumentText.document
    ).filter(
        DocumentText.document_id == document_id,
        DocumentText.document.has(user_id=current_user.id)
    ).first()
    
    if not document_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or extracted text not found"
        )
    
    # Create basic profile from extracted text
    # In a full implementation, you might use LLM to parse this
    profile = Profile(
        user_id=current_user.id,
        document_id=document_id,
        full_text=document_text.extracted_text,
        skills=[],
        education=[],
        experience=[],
        projects=[]
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return ProfileResponse.from_orm(profile)


@router.get("/", response_model=List[ProfileResponse])
async def list_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all profiles for current user."""
    profiles = db.query(Profile).filter(
        Profile.user_id == current_user.id
    ).order_by(Profile.created_at.desc()).all()
    
    return [ProfileResponse.from_orm(prof) for prof in profiles]


@router.get("/latest", response_model=ProfileResponse)
async def get_latest_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the most recent profile for current user."""
    profile = db.query(Profile).filter(
        Profile.user_id == current_user.id
    ).order_by(Profile.created_at.desc()).first()

    print("latest profile: ", profile)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found. Please create one first."
        )
    
    return ProfileResponse.from_orm(profile)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific profile."""
    profile = db.query(Profile).filter(
        Profile.id == profile_id,
        Profile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse.from_orm(profile)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a profile."""
    profile = db.query(Profile).filter(
        Profile.id == profile_id,
        Profile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return ProfileResponse.from_orm(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a profile."""
    profile = db.query(Profile).filter(
        Profile.id == profile_id,
        Profile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    db.delete(profile)
    db.commit()
    
    return None
