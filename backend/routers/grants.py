# routers/grants.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from database import get_db
from models.profile import Profile
from models.user import User
from schemas.grants import (
    GrantSuggestionsResponse,
    GrantsSearchRequest,
    GrantsSearchResponse,
)
from services.grants_service import grants_service
from services.grants_client import (
    GrantsAuthError,
    GrantsUpstreamError,
    GrantsValidationError,
    GrantsClientError,
)

router = APIRouter(prefix="/grants", tags=["grants"])


@router.get("/suggestions", response_model=GrantSuggestionsResponse)
async def get_grant_suggestions(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    except GrantsAuthError as e:
        # server configuration issue
        raise HTTPException(status_code=500, detail=str(e))
    except GrantsUpstreamError as e:
        # upstream returned an error (include upstream status and short body)
        body_snip = (e.body[:100] + "...") if getattr(e, "body", None) else None
        raise HTTPException(
            status_code=502,
            detail=f"Simpler.Grants upstream error (status={e.status_code}): {e}. body={body_snip}",
        )
    except GrantsValidationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except GrantsClientError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/search", response_model=GrantsSearchResponse)
async def search_grants(
    body: GrantsSearchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    User-driven endpoint:
    - Frontend passes query + filters (type, status, agency, etc.)
    - Backend proxies to Simpler.Grants.gov and returns normalized results.
    """
    try:
        return await grants_service.search_grants(body)
    except GrantsAuthError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except GrantsUpstreamError as e:
        body_snip = (e.body[:200] + "...") if getattr(e, "body", None) else None
        raise HTTPException(
            status_code=502,
            detail=f"Simpler.Grants upstream error (status={e.status_code}): {e}. body={body_snip}",
        )
    except GrantsValidationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except GrantsClientError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")