"""
Opportunities router for managing job/internship opportunities.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user import User
from models.opportunity import Opportunity, OpportunityRequirement, OpportunityStatus
from models.profile import Profile
from schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    OpportunityAnalysisRequest,
    OpportunityAnalysisResponse
)
from utils.auth import get_current_user
from services.llm_client import llm_client

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opp_data: OpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new opportunity."""
    opportunity = Opportunity(
        user_id=current_user.id,
        title=opp_data.title,
        organization=opp_data.organization,
        url=opp_data.url,
        description=opp_data.description,
        deadline=opp_data.deadline,
        status=OpportunityStatus.TO_APPLY
    )
    
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    
    return OpportunityResponse.from_orm(opportunity)


@router.post("/analyze", response_model=OpportunityAnalysisResponse)
async def analyze_opportunity(
    analysis_request: OpportunityAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze fit between user profile and opportunity."""
    # Get profile
    if analysis_request.profile_id:
        profile = db.query(Profile).filter(
            Profile.id == analysis_request.profile_id,
            Profile.user_id == current_user.id
        ).first()
    else:
        # Get latest profile
        profile = db.query(Profile).filter(
            Profile.user_id == current_user.id
        ).order_by(Profile.created_at.desc()).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found. Please create a profile first."
        )
    
    # Analyze fit using LLM
    try:
        result = await llm_client.analyze_fit(
            profile_text=profile.full_text,
            opportunity_text=analysis_request.opportunity_text
        )
        
        return OpportunityAnalysisResponse(
            fit_score=result["fit_score"],
            fit_analysis=result["fit_analysis"],
            extracted_requirements=result.get("extracted_requirements", [])
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/{opportunity_id}/analyze", response_model=OpportunityResponse)
async def analyze_existing_opportunity(
    opportunity_id: int,
    profile_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze an existing opportunity and update it with fit score."""
    # Get opportunity
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.user_id == current_user.id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Get profile
    if profile_id:
        profile = db.query(Profile).filter(
            Profile.id == profile_id,
            Profile.user_id == current_user.id
        ).first()
    else:
        profile = db.query(Profile).filter(
            Profile.user_id == current_user.id
        ).order_by(Profile.created_at.desc()).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found"
        )
    
    # Analyze
    try:
        result = await llm_client.analyze_fit(
            profile_text=profile.full_text,
            opportunity_text=opportunity.description
        )
        
        # Update opportunity
        opportunity.fit_score = result["fit_score"]
        opportunity.fit_analysis = result["fit_analysis"]
        
        # Add requirements
        for req_data in result.get("extracted_requirements", []):
            requirement = OpportunityRequirement(
                opportunity_id=opportunity.id,
                requirement_text=req_data["requirement_text"],
                requirement_type=req_data.get("requirement_type"),
                is_mandatory=req_data.get("is_mandatory", False)
            )
            db.add(requirement)
        
        db.commit()
        db.refresh(opportunity)
        
        return OpportunityResponse.from_orm(opportunity)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/", response_model=List[OpportunityResponse])
async def list_opportunities(
    status_filter: Optional[OpportunityStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all opportunities for current user."""
    query = db.query(Opportunity).filter(Opportunity.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Opportunity.status == status_filter)
    
    opportunities = query.order_by(Opportunity.created_at.desc()).all()
    
    return [OpportunityResponse.from_orm(opp) for opp in opportunities]


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific opportunity."""
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.user_id == current_user.id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return OpportunityResponse.from_orm(opportunity)


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    opp_data: OpportunityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an opportunity."""
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.user_id == current_user.id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Update fields
    update_data = opp_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)
    
    db.commit()
    db.refresh(opportunity)
    
    return OpportunityResponse.from_orm(opportunity)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an opportunity."""
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.user_id == current_user.id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    db.delete(opportunity)
    db.commit()
    
    return None
