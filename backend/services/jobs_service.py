# services/jobs_service.py
from typing import List
from services.jobs_client import jobs_client
from services.llm_client import llm_client
from schemas.jobs import (
    JobSuggestionsResponse,
    JobSuggestion,
    JobsSearchRequest,
    JobsSearchResponse,
    JobsSearchItem,
)
import logging


class JobsService:
    """Service for all job-related logic."""
    def __init__(self):
        self.client = jobs_client

    async def get_suggestions_for_profile(
        self,
        profile_id,
        profile_text: str,
        limit: int = 10,
        country: str = "us",
    ) -> JobSuggestionsResponse:
        """
        Generate job suggestions using LLM-generated search query.
        
        Flow: LLM generates search query from profile → call Adzuna API
        """
        logger = logging.getLogger(__name__)
        
        # Generate search query using LLM (similar to grants)
        # For jobs, we want keywords like "software engineer", "data scientist", etc.
        system_prompt = '''
            You are an expert at analyzing resumes and generating job search queries.
            Generate a focused job search query that will find relevant job opportunities.
            Focus on: job title, key skills, or field of work.
            Use terms like: 'software engineer', 'data scientist', 'product manager', etc.
            Return ONLY the query text - no quotes, no explanations, no markup.
            Keep it concise (1-5 words typically).
            Example queries: "software engineer", "data scientist python", "product manager"
        '''
        
        prompt = f"Profile:\n{profile_text}\n\nGenerate a relevant job search query for this profile:"
        
        try:
            query = await llm_client.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=50,
            )
            query = query.strip().strip('"').strip("'")
            logger.info(f"LLM generated query for jobs search: '{query}'")
        except Exception as e:
            logger.error(f"Error generating query from profile: {e}")
            # Fallback: use generic search
            query = "software engineer"
        
        # Build minimal search request
        search_request = JobsSearchRequest(
            country=country,
            page=1,
            results_per_page=limit,
            what=query,
        )
        
        # Call Adzuna API
        api_result = await self.client.search(search_request)
        
        # Map API response to suggestions
        items = [
            JobSuggestion(
                id=job.id,
                title=job.title,
                company=job.company.display_name if job.company else None,
                location=job.location.display_name if job.location else None,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                description=job.description,
                redirect_url=job.redirect_url,
                created=job.created,
                category=job.category.label if job.category else None,
            )
            for job in api_result.results
        ]
        
        return JobSuggestionsResponse(
            profile_id=str(profile_id),
            query_keywords=query.split()[:6],
            total_records=api_result.count or len(items),
            items=items,
        )

    async def search_jobs(
        self,
        request: JobsSearchRequest,
    ) -> JobsSearchResponse:
        """
        Used by /jobs/search: user-driven search with explicit parameters.
        """
        api_result = await self.client.search(request)
        
        items = [
            JobsSearchItem(
                id=job.id,
                title=job.title,
                company=job.company.display_name if job.company else None,
                location=job.location.display_name if job.location else None,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                description=job.description,
                redirect_url=job.redirect_url,
                created=job.created,
                category=job.category.label if job.category else None,
                contract_time=job.contract_time,
                contract_type=job.contract_type,
            )
            for job in api_result.results
        ]
        
        return JobsSearchResponse(
            total_records=api_result.count or len(items),
            page=request.page or 1,
            results_per_page=request.results_per_page or 10,
            items=items,
        )


# Global service instance
jobs_service = JobsService()



