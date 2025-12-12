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
        print("profile text in service:", profile_text)
        print("priofile id in service:", profile_id)
        # Prefer asking the LLM to construct a full GrantsSearchRequest payload
        # that can be sent directly to the /grants/search path. If that fails,
        # fall back to the older keyword-based search.
        payload = None
        keywords = []
        try:
            payload = await llm_client.generate_grants_search_request_from_profile(profile_text, max_results=limit)
            print("LLM generated payload:", payload)
            # Validate/convert to GrantsSearchRequest (Pydantic v2)
            try:
                request_model = GrantsSearchRequest.model_validate(payload)
            except Exception:
                # treat as failure and fall back
                request_model = None

            if request_model is not None:
                api_result = await self.client.search(request_model)
                # derive keywords for response metadata
                q = payload.get("query") if isinstance(payload, dict) else None
                if q:
                    keywords = q.split()[:6]
            else:
                raise Exception("LLM payload validation failed")

        except Exception:
            # Fallback to keyword generation then search
            try:
                keywords = await llm_client.generate_keywords_from_profile(profile_text)
            except Exception:
                # simple token fallback
                import re
                text = re.sub(r"[^a-zA-Z0-9\s]", " ", profile_text or "")
                tokens = [t.lower() for t in text.split() if len(t) > 3]
                stop = {
                    "and",
                    "the",
                    "with",
                    "that",
                    "this",
                    "from",
                    "their",
                    "they",
                    "have",
                    "will",
                    "which",
                }
                keywords = []
                for t in tokens:
                    if t in stop:
                        continue
                    if t not in keywords:
                        keywords.append(t)
                    if len(keywords) >= 6:
                        break

            api_result = await self.client.search_grants_for_keywords(
                keywords=keywords,
                limit=limit,
                page=1,
            )

        items = []
        for opp in getattr(api_result, "data", []) or []:
            try:
                items.append(
                    GrantSuggestion(
                        opportunity_id=getattr(opp, "opportunity_id", ""),
                        opportunity_number=getattr(opp, "opportunity_number", ""),
                        title=getattr(opp, "opportunity_title", getattr(opp, "title", "")),
                        agency_name=getattr(opp, "agency_name", ""),
                        post_date=getattr(opp, "post_date", None),
                        close_date=getattr(opp, "close_date", None),
                        opportunity_status=getattr(opp, "opportunity_status", ""),
                    )
                )
            except Exception:
                # skip malformed items but continue
                continue

        applied_filters = {
            "opportunity_status": ["posted", "forecasted"],
            "funding_instrument": ["grant"],
            "applicant_type": [
                "individuals",
                "public_and_state_institutions_of_higher_education",
            ],
        }

        total_records = 0
        try:
            total_records = getattr(api_result, "pagination_info", {}).get("total_records") if isinstance(getattr(api_result, "pagination_info", None), dict) else getattr(getattr(api_result, "pagination_info", None), "total_records", 0)
        except Exception:
            total_records = 0

        return GrantSuggestionsResponse(
            profile_id=str(profile_id) if profile_id is not None else None,
            query_keywords=keywords,
            applied_filters=applied_filters,
            total_records=total_records or len(items),
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
