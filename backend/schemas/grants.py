# backend/schemas/grants.py

from datetime import date
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# ---------- Pagination / sorting ----------

class SortOption(BaseModel):
    order_by: str = Field(default="relevancy")
    sort_direction: Literal["ascending", "descending"] = "descending"


class PaginationReq(BaseModel):
    page_offset: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort_order: List[SortOption] = Field(default_factory=list)


# ---------- Filter helper models ----------

class OneOfFilter(BaseModel):
    """Generic string enum filter: { 'one_of': ['posted', 'forecasted'] }"""
    one_of: List[str] = Field(default_factory=list)


class BoolOneOfFilter(BaseModel):
    """Boolean version: { 'one_of': [true] }"""
    one_of: List[bool] = Field(default_factory=list)


class DateRangeFilter(BaseModel):
    """Date range filter: { 'start_date': '2024-01-01', 'end_date': '2024-12-31' }"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class NumberRangeFilter(BaseModel):
    """Numeric range filter: { 'min': 10000, 'max': 50000 }"""
    min: Optional[float] = None
    max: Optional[float] = None


class Filters(BaseModel):
    """
    Filters for Simpler.Grants search.

    These mirror the docs:
    - opportunity_status: { "one_of": ["posted", "forecasted"] }
    - funding_instrument: { "one_of": ["grant"] }
    - applicant_type: { "one_of": ["individuals"] }
    - post_date / close_date: { "start_date": "...", "end_date": "..." }
    - award_floor / award_ceiling: { "min": ..., "max": ... }
    - is_cost_sharing: { "one_of": [true] }
    """

    opportunity_status: Optional[OneOfFilter] = None
    funding_instrument: Optional[OneOfFilter] = None
    applicant_type: Optional[OneOfFilter] = None

    # Optional extras for user search:
    agency: Optional[OneOfFilter] = None
    funding_category: Optional[OneOfFilter] = None
    post_date: Optional[DateRangeFilter] = None
    close_date: Optional[DateRangeFilter] = None
    award_floor: Optional[NumberRangeFilter] = None
    award_ceiling: Optional[NumberRangeFilter] = None
    is_cost_sharing: Optional[BoolOneOfFilter] = None

    class Config:
        extra = "ignore"  # ignore unknown filter fields instead of erroring


# ---------- Suggestions (AI-driven) ----------

class GrantSuggestion(BaseModel):
    opportunity_id: str
    opportunity_number: str
    title: str
    agency_name: str
    post_date: Optional[str] = None
    close_date: Optional[str] = None
    opportunity_status: str


class GrantSuggestionsResponse(BaseModel):
    profile_id: Optional[str] = None
    query_keywords: List[str]
    applied_filters: Dict[str, Any]
    total_records: int
    items: List[GrantSuggestion]


# ---------- Search endpoint request/response ----------

class GrantsSearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[Filters] = None
    pagination: PaginationReq = Field(
        default_factory=lambda: PaginationReq(
            page_offset=1,
            page_size=10,
            sort_order=[],
        )
    )

    class Config:
        # This controls the example shown in Swagger /docs
        json_schema_extra = {
            "example": {
                "query": "machine learning fellowship",
                "filters": {
                    "opportunity_status": {"one_of": ["posted"]},
                    "funding_instrument": {"one_of": ["grant"]},
                    "applicant_type": {"one_of": ["individuals"]},
                    "post_date": {
                        "start_date": "2024-01-01",
                        "end_date": "2024-12-31",
                    },
                },
                "pagination": {
                    "page_offset": 1,
                    "page_size": 10,
                    "sort_order": [
                        {
                            "order_by": "post_date",
                            "sort_direction": "descending",
                        }
                    ],
                },
            }
        }


class GrantsSearchItem(BaseModel):
    opportunity_id: str
    opportunity_number: str
    title: str
    agency_name: str
    agency_code: Optional[str] = None

    post_date: Optional[str] = None
    close_date: Optional[str] = None
    opportunity_status: str

    funding_instruments: Optional[List[str]] = None
    funding_categories: Optional[List[str]] = None
    award_floor: Optional[float] = None
    award_ceiling: Optional[float] = None
    is_cost_sharing: Optional[bool] = None



class GrantsSearchResponse(BaseModel):
    total_records: int
    page_offset: int
    page_size: int
    items: List[GrantsSearchItem]


# ---------- Raw API response models (from Simpler.Grants) ----------

class GrantAPIOpportunity(BaseModel):
    opportunity_id: str
    opportunity_number: str
    opportunity_title: str
    agency_code: Optional[str] = None
    agency_name: str
    post_date: Optional[str] = None
    close_date: Optional[str] = None
    opportunity_status: str

    # Additional fields present in the upstream response
    funding_instrument: Optional[str] = None
    funding_category: Optional[str] = None
    award_floor: Optional[float] = None
    award_ceiling: Optional[float] = None
    estimated_total_program_funding: Optional[float] = None
    expected_number_of_awards: Optional[int] = None
    applicant_types: Optional[List[str]] = None

    # summary is an object in real upstream responses — keep as dict (or define a model)
    summary: Optional[Dict[str, Any]] = None
    # convenience: expose a flattened summary_description if you often need the text
    summary_description: Optional[str] = None

    is_cost_sharing: Optional[bool] = None

    class Config:
        extra = "allow"

class PaginationInfo(BaseModel):
    page_offset: int
    page_size: int
    total_pages: int
    total_records: int


class GrantsAPISearchResponse(BaseModel):
    message: str
    data: List[GrantAPIOpportunity]
    pagination_info: PaginationInfo
