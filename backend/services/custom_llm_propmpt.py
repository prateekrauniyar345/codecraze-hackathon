"""Custom LLM prompts for Grants payload generation.

This module centralizes system and user instructions used by the LLM for
constructing search payloads and other downstream tasks. Keep prompts
here so they can be iterated independently from code.
"""
from typing import Tuple


# System-level prompt for generating a GrantsSearchRequest payload.
# This prompt is intentionally strict about output format (JSON only)
# and enumerates required fields, types and validation rules.
SEARCH_PAYLOAD_SYSTEM = (
    "You are an expert data engineer building search payloads for the Simpler.Grants "
    "API. Always return a single valid JSON object and nothing else (no markdown, no "
    "explanations). The JSON must conform to the GrantsSearchRequest schema: it may "
    "contain `query` (string or null), `filters` (object) and `pagination` (object).")


# User-facing instructions template that will be combined with profile text.
# It describes allowed filter fields, types and examples.
SEARCH_PAYLOAD_INSTRUCTIONS = (
    "Construct a GrantsSearchRequest JSON payload that will find grant opportunities "
    "matching the candidate profile provided. Requirements:\n"
    "1) `query`: optional string. If present it must be at least 5 characters. If no "
    "useful free-text query can be constructed, set `query` to null. Avoid very short "
    "tokens like 'research' alone if they are unlikely to narrow results. Collapse "
    "whitespace and do not include punctuation-only tokens. Maximum query length: 500 chars.\n"
    "2) `filters`: optional object. Use these keys when relevant: `opportunity_status`, "
    "`funding_instrument`, `applicant_type`, `agency`, `funding_category`, `post_date`, "
    "`close_date`, `award_floor`, `award_ceiling`, `is_cost_sharing`. For enum filters use "
    "the shape {\"one_of\": [ ... ] }. For date ranges use {\"start_date\": \"YYYY-MM-DD\", "
    "\"end_date\": \"YYYY-MM-DD\"}. For numeric ranges use {\"min\": number, \"max\": number}.\n"
    "3) `pagination`: REQUIRED. Provide `page_offset` (1..), `page_size` (1..100) and a non-empty "
    "`sort_order` array. Prefer [{\"order_by\": \"post_date\", \"sort_direction\": \"descending\"}].\n"
    "4) Output only the minimal JSON object; do not include analysis or extra keys. Dates must be "
    "ISO format (YYYY-MM-DD). Use double quotes for all JSON property names and strings.\n\n"
    "Return the JSON only."
)


# Small example the LLM can follow (kept short and valid).
SEARCH_PAYLOAD_EXAMPLE = {
    "query": "machine learning fellowship",
    "filters": {
        "opportunity_status": {"one_of": ["posted"]},
        "funding_instrument": {"one_of": ["grant"]},
        "applicant_type": {"one_of": ["individuals"]},
        "post_date": {"start_date": "2024-01-01", "end_date": "2025-01-01"}
    },
    "pagination": {
        "page_offset": 1,
        "page_size": 10,
        "sort_order": [{"order_by": "post_date", "sort_direction": "descending"}]
    }
}


def build_search_payload_prompt(profile_text: str, max_results: int = 10) -> Tuple[str, str]:
    """Return a (system_prompt, user_prompt) tuple ready to send to the LLM.

    - `profile_text` will be appended to the user prompt so the LLM has context.
    - `max_results` is substituted into the required pagination.page_size.
    """
    system = SEARCH_PAYLOAD_SYSTEM

    user = (
        SEARCH_PAYLOAD_INSTRUCTIONS
        + f"\n\nCANDIDATE PROFILE:\n{profile_text}\n\nExample payload (for reference): {SEARCH_PAYLOAD_EXAMPLE}\n\n"
        + f"Set pagination.page_size to {max_results}."
    )

    return system, user
