"""
Materials router for generating application materials.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User
from models.opportunity import Opportunity
from models.profile import Profile
from models.material import GeneratedMaterial, MaterialType
from schemas.material import MaterialGenerateRequest, MaterialResponse
from services.auth_services import get_current_user
from services.llm_client import llm_client

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.post("/generate", response_model=List[MaterialResponse], status_code=status.HTTP_201_CREATED)
async def generate_materials(
    request: MaterialGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate application materials for an opportunity."""
    # Get opportunity
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == request.opportunity_id,
        Opportunity.user_id == current_user.id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Get profile
    if request.profile_id:
        profile = db.query(Profile).filter(
            Profile.id == request.profile_id,
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
    
    # Prepare fit analysis
    fit_analysis = opportunity.fit_analysis or {}
    
    generated_materials = []
    
    try:
        for material_type in request.material_types:
            content = ""
            
            if material_type == MaterialType.EMAIL:
                content = await llm_client.generate_email(
                    profile_text=profile.full_text,
                    opportunity_text=opportunity.description,
                    fit_analysis=fit_analysis
                )
            
            elif material_type == MaterialType.SUBJECT_LINE:
                content = await llm_client.generate_subject_line(
                    profile_text=profile.full_text,
                    opportunity_text=opportunity.description
                )
            
            elif material_type == MaterialType.SOP_PARAGRAPH:
                content = await llm_client.generate_sop_paragraph(
                    profile_text=profile.full_text,
                    opportunity_text=opportunity.description,
                    fit_analysis=fit_analysis
                )
            
            elif material_type == MaterialType.FIT_BULLETS:
                content = await llm_client.generate_fit_bullets(
                    profile_text=profile.full_text,
                    opportunity_text=opportunity.description,
                    fit_analysis=fit_analysis
                )
            
            # Save generated material
            material = GeneratedMaterial(
                opportunity_id=opportunity.id,
                user_id=current_user.id,
                material_type=material_type,
                content=content
            )
            
            db.add(material)
            generated_materials.append(material)
        
        db.commit()
        
        # Refresh all materials
        for material in generated_materials:
            db.refresh(material)
        
        return [MaterialResponse.from_orm(mat) for mat in generated_materials]
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Material generation failed: {str(e)}"
        )


@router.get("/opportunity/{opportunity_id}", response_model=List[MaterialResponse])
async def get_materials_for_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all materials for an opportunity."""
    # Verify opportunity belongs to user
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.user_id == current_user.id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    materials = db.query(GeneratedMaterial).filter(
        GeneratedMaterial.opportunity_id == opportunity_id
    ).order_by(GeneratedMaterial.created_at.desc()).all()
    
    return [MaterialResponse.from_orm(mat) for mat in materials]


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific generated material."""
    material = db.query(GeneratedMaterial).filter(
        GeneratedMaterial.id == material_id,
        GeneratedMaterial.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    return MaterialResponse.from_orm(material)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a generated material."""
    material = db.query(GeneratedMaterial).filter(
        GeneratedMaterial.id == material_id,
        GeneratedMaterial.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    db.delete(material)
    db.commit()
    
    return None
