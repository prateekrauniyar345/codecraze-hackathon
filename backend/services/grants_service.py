# services/grants_service.py
from typing import List
import re
from collections import Counter

from services.grants_client import grants_client, SearchRequest
from schemas.grants import (
    GrantSuggestionsResponse,
    GrantSuggestion,
    GrantsSearchRequest,
    GrantsSearchResponse,
    GrantsSearchItem,
)


_STOPWORDS = {
    "and", "or", "the", "a", "an", "for", "of", "to", "in", "on",
    "with", "at", "by", "from", "as", "is", "are", "was", "were",
    "this", "that", "these", "those", "my", "your", "our", "their",
    "i", "me", "we", "you", "they", "it", "be", "have", "has", "had",
    "research", "project", "projects", "experience", "skills",
}


def _extract_keywords_from_profile(text: str, max_keywords: int = 8) -> List[str]:
    """
    Simple keyword extractor for suggestions.
    Later you can swap this for an LLM-based keyword generator if you want.
    """
    cleaned = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
    tokens = [
        t for t in cleaned.split()
        if t and t not in _STOPWORDS and len(t) > 3
    ]
    if not tokens:
        return []
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(max_keywords)]


class GrantsService:
    """Service for all grant-related logic."""
    def __init__(self):
        self.client = grants_client

    async def get_suggestions_for_profile(
        self,
        profile_id,
        profile_text: str,
        limit: int = 10,
    ) -> GrantSuggestionsResponse:
        """
        Used by AI / internal flows: build query from profile text, hit Simpler.Grants,
        and return a structured suggestion payload.
        """
        keywords = _extract_keywords_from_profile(profile_text, max_keywords=8)

        api_result = await self.client.search_grants_for_keywords(
            keywords=keywords,
            limit=limit,
            page=1,
        )

        items = [
            GrantSuggestion(
                opportunity_id=opp.opportunity_id,
                opportunity_number=opp.opportunity_number,
                title=opp.opportunity_title,
                agency_name=opp.agency_name,
                post_date=opp.post_date,
                close_date=opp.close_date,
                opportunity_status=opp.opportunity_status,
            )
            for opp in api_result.data
        ]

        applied_filters = {
            "opportunity_status": ["posted", "forecasted"],
            "funding_instrument": ["grant"],
            "applicant_type": [
                "individuals",
                "public_and_state_institutions_of_higher_education",
            ],
        }

        return GrantSuggestionsResponse(
            profile_id=profile_id,
            query_keywords=keywords,
            applied_filters=applied_filters,
            total_records=api_result.pagination_info.total_records,
            items=items,
        )

    async def search_grants(
        self,
        request: GrantsSearchRequest,
    ) -> GrantsSearchResponse:
        """
        Used by /grants/search: user-driven search with explicit filters.
        """
        # Convert our API schema into the core SearchRequest model
        core_request = SearchRequest(
            query=request.query,
            filters=request.filters,
            pagination=request.pagination,
        )
        api_result = await self.client.search(core_request)

        items = [
            GrantsSearchItem(
                opportunity_id=opp.opportunity_id,
                opportunity_number=opp.opportunity_number,
                title=opp.opportunity_title,
                agency_name=opp.agency_name,
                post_date=opp.post_date,
                close_date=opp.close_date,
                opportunity_status=opp.opportunity_status,
            )
            for opp in api_result.data
        ]

        return GrantsSearchResponse(
            total_records=api_result.pagination_info.total_records,
            page_offset=api_result.pagination_info.page_offset,
            page_size=api_result.pagination_info.page_size,
            items=items,
        )


# Global service instance
grants_service = GrantsService()
