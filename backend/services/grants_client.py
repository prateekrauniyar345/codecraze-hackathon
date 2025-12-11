# services/grants_client.py
"""
Client for Simpler.Grants.gov API with retry logic and async HTTP.
"""
from typing import List, Optional, Dict, Any
import httpx
from pydantic import ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from schemas.grants import (
    GrantsAPISearchResponse,
    GrantsSearchRequest,
    Filters,
    OneOfFilter,
    PaginationReq,
    SortOption,
)

from config import get_settings

settings = get_settings()

SIMPLE_GRANTS_DEFAULT_BASE_URL = "https://api.simpler.grants.gov/v1/opportunities/search"


# ----- Custom exceptions -----
class GrantsClientError(Exception):
    """Base exception for grants client errors."""


class GrantsAuthError(GrantsClientError):
    """Missing or invalid API key/credentials."""


class GrantsUpstreamError(GrantsClientError):
    """Upstream HTTP error from Simpler.Grants.gov."""

    def __init__(self, status_code: int, message: str, body: Any | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class GrantsValidationError(GrantsClientError):
    """Returned when upstream response cannot be parsed/validated."""


# ---------- Client class ----------

class GrantsClient:
    """Client for interacting with the Simpler.Grants.gov API."""

    def __init__(self) -> None:
        # Support either name in env: SIMPLE_GRANTS_API_KEY or SIMPLE_GRANTS
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
            raise GrantsAuthError(
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
    async def _post_search(self, payload: GrantsSearchRequest) -> Dict[str, Any]:
        """Low-level POST /v1/opportunities/search with retry."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    self.base_url,
                    headers=self._get_headers(),
                    json=payload.model_dump(mode="json", exclude_none=True),
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                # upstream returned 4xx/5xx
                body = None
                try:
                    body = e.response.text
                except Exception:
                    pass
                raise GrantsUpstreamError(
                    status_code=e.response.status_code if e.response is not None else 0,
                    message=f"Upstream HTTP error: {e}",
                    body=body,
                ) from e
            except httpx.HTTPError as e:
                # network / timeout / connection errors
                raise GrantsUpstreamError(
                    status_code=0,
                    message=f"HTTP error contacting Simpler.Grants: {e}",
                ) from e

    async def search(self, request: GrantsSearchRequest) -> GrantsAPISearchResponse:
        """Generic search used by /grants/search."""
        try:
            raw = await self._post_search(request)
        except GrantsClientError:
            # propagate our known client exceptions
            raise
        except Exception as e:
            # Wrap any unexpected error
            raise GrantsClientError(f"Unexpected grants client error: {e}") from e
        
        try:
            return GrantsAPISearchResponse.model_validate(raw)
        except ValidationError as e:
            import json, logging
            logger = logging.getLogger(__name__)
            # pretty-print raw response for logs
            try:
                pretty_raw = json.dumps(raw, indent=2, ensure_ascii=False)
            except Exception:
                pretty_raw = str(raw)

            logger.error("Simpler.Grants response validation failed: %s", e)
            logger.debug("Simpler.Grants raw response:\n%s", pretty_raw)

            # Attach full details to the exception for the router to return during dev
            detail = {
                "message": "Simpler.Grants response shape validation failed",
                "validation_error": e.errors() if hasattr(e, "errors") else str(e),
                "raw": raw,
            }
            gv = GrantsValidationError("Simpler.Grants response shape validation failed")
            gv.detail = detail
            gv.raw = raw
            gv.validation = e
            raise gv from e

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
            opportunity_status=OneOfFilter(one_of=["posted", "forecasted"]),
            funding_instrument=OneOfFilter(one_of=["grant"]),
            applicant_type=OneOfFilter(
                one_of=[
                    "individuals",
                    "public_and_state_institutions_of_higher_education",
                ]
            ),
        )

        payload = GrantsSearchRequest(
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