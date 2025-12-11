import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict
from enum import Enum

class SortOption(BaseModel):
    order_by: str = Field(default="relevancy")
    sort_direction: Literal["ascending", "descending"] = "descending"


class PaginationReq(BaseModel):
    page_offset: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort_order: List[SortOption]


class Filters(BaseModel):
    opportunity_status: Optional[dict] = None
    funding_instrument: Optional[dict] = None
    applicant_type: Optional[dict] = None
    # Optional extras (user search might use these):
    agency: Optional[dict] = None
    funding_category: Optional[dict] = None
    post_date: Optional[dict] = None
    close_date: Optional[dict] = None
    award_floor: Optional[dict] = None
    award_ceiling: Optional[dict] = None
    is_cost_sharing: Optional[dict] = None

    class Config:
        extra = "allow"  # allow additional filters if needed


class SearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[Filters] = None
    pagination: PaginationReq


class GrantAPIOpportunity(BaseModel):
    opportunity_id: str
    opportunity_number: str
    opportunity_title: str
    agency_name: str
    post_date: Optional[str] = None
    close_date: Optional[str] = None
    opportunity_status: str


class PaginationInfo(BaseModel):
    page_offset: int
    page_size: int
    total_pages: int
    total_records: int


class GrantsAPISearchResponse(BaseModel):
    message: str
    data: List[GrantAPIOpportunity]
    pagination_info: PaginationInfo