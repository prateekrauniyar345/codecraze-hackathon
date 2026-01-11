# backend/schemas/jobs.py

from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ---------- Search endpoint request/response ----------

class JobsSearchRequest(BaseModel):
    """Request schema for job search."""
    country: Optional[str] = Field(default="us", description="ISO country code (e.g., 'us', 'gb')")
    page: Optional[int] = Field(default=1, ge=1, description="Page number")
    results_per_page: Optional[int] = Field(default=10, ge=1, le=50, description="Results per page")
    
    # Search parameters (keeping it simple)
    what: Optional[str] = Field(None, description="Keywords to search for")
    where: Optional[str] = Field(None, description="Location/geographic center")
    distance: Optional[int] = Field(None, description="Distance in km from location")
    category: Optional[str] = Field(None, description="Job category tag")
    
    # Salary filters
    salary_min: Optional[int] = Field(None, description="Minimum salary")
    salary_max: Optional[int] = Field(None, description="Maximum salary")
    
    # Job type filters
    full_time: Optional[bool] = Field(None, description="Full time jobs only")
    part_time: Optional[bool] = Field(None, description="Part time jobs only")
    contract: Optional[bool] = Field(None, description="Contract jobs only")
    permanent: Optional[bool] = Field(None, description="Permanent jobs only")
    
    # Other filters
    max_days_old: Optional[int] = Field(None, description="Max age of job posting in days")
    sort_by: Optional[str] = Field(None, description="Sort field (e.g., 'date', 'salary', 'relevance')")
    sort_dir: Optional[str] = Field(None, description="Sort direction ('asc' or 'desc')")

    class Config:
        json_schema_extra = {
            "example": {
                "country": "us",
                "page": 1,
                "results_per_page": 10,
                "what": "software engineer",
                "where": "San Francisco",
                "salary_min": 80000,
                "full_time": True,
            }
        }


# ---------- Response models (from Adzuna API) ----------

class JobLocation(BaseModel):
    """Location information for a job."""
    display_name: Optional[str] = None
    area: Optional[List[str]] = None


class JobCategory(BaseModel):
    """Category information for a job."""
    tag: Optional[str] = None
    label: Optional[str] = None


class JobCompany(BaseModel):
    """Company information for a job."""
    display_name: Optional[str] = None
    canonical_name: Optional[str] = None
    count: Optional[int] = None
    average_salary: Optional[int] = None


class JobResult(BaseModel):
    """Individual job result from Adzuna API."""
    id: str
    title: str
    description: Optional[str] = None
    created: Optional[str] = None
    redirect_url: Optional[str] = None
    adref: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[JobLocation] = None
    category: Optional[JobCategory] = None
    company: Optional[JobCompany] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_is_predicted: Optional[str] = None
    contract_time: Optional[str] = None
    contract_type: Optional[str] = None

    class Config:
        extra = "allow"  # Allow extra fields from API


class JobsAPISearchResponse(BaseModel):
    """Raw API response from Adzuna."""
    count: Optional[int] = 0
    mean: Optional[float] = None
    results: List[JobResult] = Field(default_factory=list)


# ---------- Suggestions (AI-driven) ----------

class JobSuggestion(BaseModel):
    """Job suggestion for user."""
    id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    redirect_url: Optional[str] = None
    created: Optional[str] = None
    category: Optional[str] = None


class JobSuggestionsResponse(BaseModel):
    """Response for job suggestions endpoint."""
    profile_id: Optional[str] = None
    query_keywords: List[str] = Field(default_factory=list)
    total_records: int = 0
    items: List[JobSuggestion] = Field(default_factory=list)


# ---------- Search endpoint response ----------

class JobsSearchItem(BaseModel):
    """Job search result item."""
    id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    redirect_url: Optional[str] = None
    created: Optional[str] = None
    category: Optional[str] = None
    contract_time: Optional[str] = None
    contract_type: Optional[str] = None


class JobsSearchResponse(BaseModel):
    """Response for job search endpoint."""
    total_records: int
    page: int
    results_per_page: int
    items: List[JobsSearchItem]



