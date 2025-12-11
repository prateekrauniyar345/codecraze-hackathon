# routers/grants.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.profile import Profile
from schemas.grants import (
    GrantSuggestionsResponse,
    GrantsSearchRequest,
    GrantsSearchResponse,
)
from services.grants_service import grants_service

router = APIRouter(prefix="/grants", tags=["grants"])


@router.get("/suggestions", response_model=GrantSuggestionsResponse)
async def get_grant_suggestions(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    AI-driven endpoint:
    - Uses latest profile (from resume)
    - Extracts keywords
    - Calls Simpler.Grants.gov with opinionated filters
    - Returns suggested grant opportunities
    """

    profile: Profile | None = (
        db.query(Profile)
        .order_by(Profile.created_at.desc())
        .first()
    )

    if not profile or not profile.summary_text:
        raise HTTPException(
            status_code=400,
            detail="No profile found. Upload a resume and generate a profile first.",
        )

    try:
        return await grants_service.get_suggestions_for_profile(
            profile_id=profile.id,
            profile_text=profile.summary_text,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error getting grant suggestions: {e}",
        )


@router.post("/search", response_model=GrantsSearchResponse)
async def search_grants(
    body: GrantsSearchRequest,
):
    """
    User-driven endpoint:
    - Frontend passes query + filters (type, status, agency, etc.)
    - Backend proxies to Simpler.Grants.gov and returns normalized results.

    Example body:
    {
      "query": "machine learning",
      "filters": {
        "opportunity_status": {"one_of": ["posted"]},
        "funding_instrument": {"one_of": ["grant"]},
        "applicant_type": {"one_of": ["individuals"]}
      },
      "pagination": {
        "page_offset": 1,
        "page_size": 20,
        "sort_order": [
          {"order_by": "post_date", "sort_direction": "descending"}
        ]
      }
    }
    """
    try:
        return await grants_service.search_grants(body)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error searching grants: {e}",
        )
