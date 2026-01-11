# services/jobs_client.py
"""
Client for Adzuna Job Search API with retry logic and async HTTP.
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
from schemas.jobs import (
    JobsSearchRequest,
    JobsAPISearchResponse,
)
from config import get_settings

settings = get_settings()

ADZUNA_DEFAULT_BASE_URL = "https://api.adzuna.com/v1"


# ----- Custom exceptions -----
class JobsClientError(Exception):
    """Base exception for jobs client errors."""


class JobsAuthError(JobsClientError):
    """Missing or invalid API key/credentials."""


class JobsUpstreamError(JobsClientError):
    """Upstream HTTP error from Adzuna API."""

    def __init__(self, status_code: int, message: str, body: Any | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class JobsValidationError(JobsClientError):
    """Returned when upstream response cannot be parsed/validated."""


# ---------- Client class ----------

class JobsClient:
    """Client for interacting with the Adzuna Job Search API."""

    def __init__(self) -> None:
        # Support either name in env: ADZUNA_APP_ID or ADZUNA_APP_KEY
        self.app_id: Optional[str] = getattr(settings, "ADZUNA_APP_ID", None)
        self.app_key: Optional[str] = getattr(settings, "ADZUNA_APP_KEY", None)
        self.base_url: str = getattr(
            settings,
            "ADZUNA_BASE_URL",
            ADZUNA_DEFAULT_BASE_URL,
        )
        self.timeout: float = getattr(settings, "ADZUNA_TIMEOUT", 20.0)
        self.max_retries: int = getattr(settings, "ADZUNA_MAX_RETRIES", 3)

    def _get_auth_params(self) -> Dict[str, str]:
        """Get authentication query parameters."""
        if not self.app_id or not self.app_key:
            raise JobsAuthError(
                "Missing ADZUNA_APP_ID or ADZUNA_APP_KEY in settings / environment."
            )
        return {
            "app_id": self.app_id,
            "app_key": self.app_key,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def _get_search(
        self,
        country: str,
        page: int,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Low-level GET /jobs/{country}/search/{page} with retry."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Add auth params
                query_params = {**self._get_auth_params(), **params}
                
                # Build URL - Adzuna API format: /v1/api/jobs/{country}/search/{page}
                # Ensure base_url doesn't have trailing slash
                base = self.base_url.rstrip('/')
                url = f"{base}/api/jobs/{country}/search/{page}"
                
                # Debug logging
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Adzuna API request URL: {url}")
                logger.debug(f"Adzuna API request params: {list(query_params.keys())}")
                
                resp = await client.get(url, params=query_params)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                # upstream returned 4xx/5xx
                body = None
                try:
                    body = e.response.text
                except Exception:
                    pass
                
                # Handle specific Adzuna error codes
                if e.response.status_code == 410:
                    raise JobsAuthError(
                        f"Adzuna API authorization failed: {e}"
                    ) from e
                elif e.response.status_code == 400:
                    raise JobsValidationError(
                        f"Invalid request parameters: {e}"
                    ) from e
                else:
                    raise JobsUpstreamError(
                        status_code=e.response.status_code if e.response is not None else 0,
                        message=f"Upstream HTTP error: {e}",
                        body=body,
                    ) from e
            except httpx.HTTPError as e:
                # network / timeout / connection errors
                raise JobsUpstreamError(
                    status_code=0,
                    message=f"HTTP error contacting Adzuna: {e}",
                ) from e

    async def search(self, request: JobsSearchRequest) -> JobsAPISearchResponse:
        """Generic search used by /jobs/search."""
        try:
            # Build query parameters from request
            params = {}
            
            # Basic search parameters (keep it simple)
            if request.what:
                params["what"] = request.what
            if request.where:
                params["where"] = request.where
            if request.distance:
                params["distance"] = request.distance
            if request.category:
                params["category"] = request.category
            if request.salary_min:
                params["salary_min"] = request.salary_min
            if request.salary_max:
                params["salary_max"] = request.salary_max
            if request.full_time:
                params["full_time"] = "1" if request.full_time else "0"
            if request.part_time:
                params["part_time"] = "1" if request.part_time else "0"
            if request.contract:
                params["contract"] = "1" if request.contract else "0"
            if request.permanent:
                params["permanent"] = "1" if request.permanent else "0"
            if request.max_days_old:
                params["max_days_old"] = request.max_days_old
            if request.sort_by:
                params["sort_by"] = request.sort_by
            if request.sort_dir:
                params["sort_dir"] = request.sort_dir
            
            # Pagination
            params["results_per_page"] = request.results_per_page or 10
            
            # Default country to 'us' if not specified
            country = request.country or "us"
            page = request.page or 1
            
            raw = await self._get_search(country, page, params)
        except JobsClientError:
            # propagate our known client exceptions
            raise
        except Exception as e:
            # Wrap any unexpected error
            raise JobsClientError(f"Unexpected jobs client error: {e}") from e
        
        try:
            return JobsAPISearchResponse.model_validate(raw)
        except ValidationError as e:
            import json, logging
            logger = logging.getLogger(__name__)
            # pretty-print raw response for logs
            try:
                pretty_raw = json.dumps(raw, indent=2, ensure_ascii=False)
            except Exception:
                pretty_raw = str(raw)

            logger.error("Adzuna response validation failed: %s", e)
            logger.debug("Adzuna raw response:\n%s", pretty_raw)

            # Attach full details to the exception for the router to return during dev
            detail = {
                "message": "Adzuna response shape validation failed",
                "validation_error": e.errors() if hasattr(e, "errors") else str(e),
                "raw": raw,
            }
            jv = JobsValidationError("Adzuna response shape validation failed")
            jv.detail = detail
            jv.raw = raw
            jv.validation = e
            raise jv from e


# Global client instance (same pattern as grants_client)
jobs_client = JobsClient()

