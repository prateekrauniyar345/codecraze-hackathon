# schemas/grants.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from models.grants import Filters, PaginationReq  


class GrantSuggestion(BaseModel):
    opportunity_id: str
    opportunity_number: str
    title: str
    agency_name: str
    post_date: Optional[str] = None
    close_date: Optional[str] = None
    opportunity_status: str


class GrantSuggestionsResponse(BaseModel):
    profile_id: Optional[UUID] = None
    query_keywords: List[str]
    applied_filters: Dict[str, Any]
    total_records: int
    items: List[GrantSuggestion]


# --- Search endpoint request/response --- #

class GrantsSearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[Filters] = None
    pagination: PaginationReq = Field(
        default_factory=lambda: PaginationReq(page_offset=1, page_size=10, sort_order=[])
    )


class GrantsSearchItem(BaseModel):
    opportunity_id: str
    opportunity_number: str
    title: str
    agency_name: str
    post_date: Optional[str] = None
    close_date: Optional[str] = None
    opportunity_status: str


class GrantsSearchResponse(BaseModel):
    total_records: int
    page_offset: int
    page_size: int
    items: List[GrantsSearchItem]
