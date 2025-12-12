# services/grants_service.py
from typing import List
from services.grants_client import grants_client
from services.llm_client import llm_client
from schemas.grants import (
    GrantSuggestionsResponse,
    GrantSuggestion,
    GrantsSearchRequest,
    GrantsSearchResponse,
    GrantsSearchItem,
)
from schemas.grants import Filters, OneOfFilter, PaginationReq, SortOption
import logging


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
        Generate grant suggestions using LLM-generated query.
        
        Flow: LLM generates query string → build minimal search payload → call Simpler.Grants API
        """
        logger = logging.getLogger(__name__)
        
        # Generate query using LLM (5-100 chars per API spec)
        query = await llm_client.generate_query_param_from_profile(profile_text)
        print("generated query in grants_service:", query)
        logger.info(f"LLM generated query for grants search: '{query}'")

        # Build minimal payload: only query + required pagination
        payload = GrantsSearchRequest(
            query=query,
            pagination=PaginationReq(
                page_offset=1,
                page_size=limit,
                sort_order=[SortOption(order_by="post_date", sort_direction="descending")],
            ),
        )

        # Call upstream API
        api_result = await self.client.search(payload)

        # Map API response to suggestions
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

        return GrantSuggestionsResponse(
            profile_id=str(profile_id),
            query_keywords=query.split()[:6],
            applied_filters={},  # No filters applied in suggestion mode
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
        api_result = await self.client.search(request)

        items = [
            GrantsSearchItem(
                opportunity_id=opp.opportunity_id,
                opportunity_number=opp.opportunity_number,
                title=opp.opportunity_title,
                agency_name=opp.agency_name,
                agency_code=opp.agency_code,

                # pull from summary, not top level:
                post_date=opp.summary.get("post_date"),
                close_date=opp.summary.get("close_date"),

                opportunity_status=opp.opportunity_status,

                # also from summary:
                funding_instruments=opp.summary.get("funding_instruments"),
                funding_categories=opp.summary.get("funding_categories"),
                award_flooropp=opp.summary.get("award_floor"),
                award_ceiling=opp.summary.get("award_ceiling"),
                is_cost_sharing=opp.summary.get("is_cost_sharing"),
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
