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
                # Dump the Pydantic model to plain dict and sanitize
                data = payload.model_dump(mode="json", exclude_none=True)

                # Sanitize 'query' to avoid upstream 422s (API spec: 5-100 chars)
                q = data.get("query")
                if isinstance(q, str):
                    q = q.strip()
                    if len(q) == 0 or len(q) < 5:
                        # remove too-short queries to avoid upstream validation errors
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.debug("Stripping too-short 'query' before upstream call: '%s'", q)
                        data.pop("query", None)
                    elif len(q) > 100:
                        # API spec: max query length is 100 chars
                        data["query"] = q[:100]

                # Ensure pagination.sort_order exists for upstream
                pagination = data.get("pagination") or {}
                if not pagination.get("sort_order"):
                    pagination.setdefault("sort_order", [{"order_by": "post_date", "sort_direction": "descending"}])
                    data["pagination"] = pagination

                resp = await client.post(
                    self.base_url,
                    headers=self._get_headers(),
                    json=data,
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
        # Ensure that a default sort order is provided if none is specified
        if not request.pagination.sort_order:
            request.pagination.sort_order = [SortOption(order_by="post_date", sort_direction="descending")]
            
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




# Global client instance (same pattern as llm_client)
grants_client = GrantsClient()