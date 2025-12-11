# core/grants_client.py
"""
Client for Simpler.Grants.gov API with retry logic and async HTTP.
"""
from typing import List, Optional, Literal, Dict, Any
from models import SortOption, Filters, PaginationReq, GrantsAPISearchResponse
import httpx
from pydantic import BaseModel, Field, ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from config import get_settings

settings = get_settings()

SIMPLE_GRANTS_DEFAULT_BASE_URL = "https://api.simpler.grants.gov/v1/opportunities/search"



# ---------- Client class ----------

class GrantsClient:
    """Client for interacting with the Simpler.Grants.gov API."""

    def __init__(self) -> None:
        # Expect something like SIMPLE_GRANTS_API_KEY or SIMPLE_GRANTS in your env
        self.api_key: Optional[str] = (
            getattr(settings, "SIMPLE_GRANTS_API_KEY", None)
            or getattr(settings, "SIMPLE_GRANTS", None)
        )
        self.base_url: str = getattr(
            settings,
            "SIMPLE_GRANTS_BASE_URL",
            SIMPLE_GRANTS_DEFAULT_BASE_URL,
        )
        self.timeout: float = getattr(settings, "SIMPLE_GRANTS_TIMEOUT", 20.0)
        self.max_retries: int = getattr(settings, "SIMPLE_GRANTS_MAX_RETRIES", 3)

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise RuntimeError(
                "Missing SIMPLE_GRANTS_API_KEY (or SIMPLE_GRANTS) in settings / environment."
            )
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def _post_search(self, payload: SearchRequest) -> Dict[str, Any]:
        """Low-level POST /v1/opportunities/search with retry."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/opportunities/search",
                headers=self._get_headers(),
                json=payload.model_dump(),
            )
            resp.raise_for_status()
            return resp.json()

    async def search(self, request: SearchRequest) -> GrantsAPISearchResponse:
        """Generic search used by /grants/search."""
        try:
            raw = await self._post_search(request)
            return GrantsAPISearchResponse.model_validate(raw)
        except ValidationError as e:
            print("Simpler.Grants response validation error:", e)
            print("Raw response body:", raw if "raw" in locals() else "no response")
            raise

    async def search_grants_for_keywords(
        self,
        keywords: List[str],
        limit: int = 10,
        page: int = 1,
    ) -> GrantsAPISearchResponse:
        """
        Opinionated search used by /grants/suggestions:
         - builds query from profile keywords
         - filters to posted/forecasted grants for individuals/higher-ed
        """
        query = " ".join(keywords[:6]) if keywords else None

        filters = Filters(
            opportunity_status={"one_of": ["posted", "forecasted"]},
            funding_instrument={"one_of": ["grant"]},
            applicant_type={
                "one_of": [
                    "individuals",
                    "public_and_state_institutions_of_higher_education",
                ]
            },
        )

        payload = SearchRequest(
            query=query,
            filters=filters,
            pagination=PaginationReq(
                page_offset=page,
                page_size=limit,
                sort_order=[
                    SortOption(order_by="post_date", sort_direction="descending")
                ],
            ),
        )

        return await self.search(payload)


# Global client instance (same pattern as llm_client)
grants_client = GrantsClient()
