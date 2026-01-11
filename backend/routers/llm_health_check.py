# top imports
import logging
import time
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from services.llm_client import llm_client
from services.auth_services import get_current_user
from models.user import User

router = APIRouter(prefix="/llm", tags=["LLM Health Check"])
logger = logging.getLogger(__name__)


@router.get("/health-check", status_code=status.HTTP_200_OK)
async def llm_health_check(current_user: User = Depends(get_current_user)):
    """Health check endpoint for LLM service (protected)."""
    logger.info("LLM health check endpoint called by user id=%s", current_user.id)

    start_time = time.perf_counter()

    messages = [{"role": "user", "content": "ping"}]

    try:
        # Minimal / cheap request
        response = await llm_client._make_request(
            messages=messages,
            temperature=0.0,
            max_tokens=1,
        )

        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000.0, 2)

        # Extract message
        message = response["choices"][0]["message"]  # dict: {"role": "assistant", "content": ...}

        if message and message.get("role") == "assistant":
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "LLM service is healthy",
                    "latency_ms": latency_ms,
                    "model": llm_client.model,
                    "llm_response": message.get("content", ""),
                },
            )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service returned an unexpected response format",
        )

    except Exception as e:
        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000.0, 2)

        logger.error(f"LLM health check error: {e}")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "LLM service is unavailable",
                "latency_ms": latency_ms,
                "reason": str(e),
            },
        )
