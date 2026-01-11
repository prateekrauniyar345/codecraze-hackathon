# routers/jobs.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from database import get_db
from models.profile import Profile
from models.user import User
from schemas.jobs import (
    JobSuggestionsResponse,
    JobsSearchRequest,
    JobsSearchResponse,
)
from services.jobs_service import jobs_service
from services.jobs_client import (
    JobsAuthError,
    JobsUpstreamError,
    JobsValidationError,
    JobsClientError,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/suggestions", response_model=JobSuggestionsResponse)
async def get_job_suggestions(
    limit: int = Query(10, ge=1, le=50),
    country: str = Query("us", description="ISO country code (e.g., 'us', 'gb')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI-driven endpoint:
    - Uses latest profile (from resume)
    - Extracts keywords using LLM
    - Calls Adzuna API with generated query
    - Returns suggested job opportunities
    """
    profile: Profile | None = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .order_by(Profile.created_at.desc())
        .first()
    )

    if not profile or not profile.full_text:
        raise HTTPException(
            status_code=400,
            detail="No profile found. Upload a resume and generate a profile first.",
        )

    try:
        return await jobs_service.get_suggestions_for_profile(
            profile_id=profile.id,
            profile_text=profile.full_text,
            limit=limit,
            country=country,
        )
    except JobsAuthError as e:
        # server configuration issue
        raise HTTPException(status_code=500, detail=str(e))
    except JobsUpstreamError as e:
        # upstream returned an error (include upstream status and short body)
        body_snip = (e.body[:100] + "...") if getattr(e, "body", None) else None
        raise HTTPException(
            status_code=502,
            detail=f"Adzuna upstream error (status={e.status_code}): {e}. body={body_snip}",
        )
    except JobsValidationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except JobsClientError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/search", response_model=JobsSearchResponse)
async def search_jobs(
    body: JobsSearchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    User-driven endpoint:
    - Frontend passes search parameters (what, where, filters, etc.)
    - Backend proxies to Adzuna API and returns normalized results.
    """
    try:
        return await jobs_service.search_jobs(body)
    except JobsAuthError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except JobsUpstreamError as e:
        body_snip = (e.body[:200] + "...") if getattr(e, "body", None) else None
        raise HTTPException(
            status_code=502,
            detail=f"Adzuna upstream error (status={e.status_code}): {e}. body={body_snip}",
        )
    except JobsValidationError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except JobsClientError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")



