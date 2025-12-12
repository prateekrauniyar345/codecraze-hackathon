"""
LLM client for OpenRouter API with retry logic and error handling.
"""
import httpx
import json
from typing import Dict, Any, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from config import get_settings
from services.custom_llm_propmpt import build_search_payload_prompt
import logging
import ast

settings = get_settings()


class LLMClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.max_retries = settings.LLM_MAX_RETRIES
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        print("llm client api key is : ", self.api_key)
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://scholarsense.app",
            "X-Title": "ScholarSense"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
    )
    async def _make_request(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to OpenRouter API with retry logic.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            response_format: Optional format specification (e.g., {"type": "json_object"})
            
        Returns:
            API response as dictionary
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if response_format:
                payload["response_format"] = response_format
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        json_mode: bool = False
    ) -> str:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            json_mode: Whether to request JSON response
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response_format = {"type": "json_object"} if json_mode else None
        
        try:
            response = await self._make_request(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )
            
            content = response["choices"][0]["message"]["content"]
            return content.strip()
        
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    async def analyze_fit(
        self,
        profile_text: str,
        opportunity_text: str
    ) -> Dict[str, Any]:
        """
        Analyze fit between profile and opportunity.
        
        Args:
            profile_text: User's profile/resume text
            opportunity_text: Opportunity description
            
        Returns:
            Dictionary with fit_score and fit_analysis
        """
        system_prompt = """You are an expert career advisor and application strategist. 
                            Analyze the fit between a candidate's profile and an opportunity.
                            You must respond with valid JSON only, following this exact structure:
                            {
                            "fit_score": <integer 0-100>,
                            "fit_analysis": {
                                "overall_fit": <integer 0-100>,
                                "strengths": [<list of specific matching qualifications>],
                                "gaps": [<list of missing qualifications or weaknesses>],
                                "recommendations": [<list of strategic recommendations for the application>]
                            },
                            "extracted_requirements": [
                                {
                                "requirement_text": "<requirement>",
                                "requirement_type": "<type: education|technical|experience|other>",
                                "is_mandatory": <boolean>
                                }
                            ]
                            }

                            Be specific and reference actual details from both texts. Fit score should be realistic and well-calibrated."""

        prompt = f"""Analyze the fit between this candidate profile and opportunity.

                    CANDIDATE PROFILE:
                    {profile_text}

                    OPPORTUNITY:
                    {opportunity_text}

                    Provide detailed analysis in JSON format as specified."""

        try:
            response_text = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000,
                json_mode=True
            )
            
            # Parse JSON response
            result = json.loads(response_text)
            
            # Validate required fields
            if "fit_score" not in result or "fit_analysis" not in result:
                raise ValueError("Invalid response format from LLM")
            
            return result
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM JSON response: {str(e)}")
        except Exception as e:
            raise Exception(f"Fit analysis failed: {str(e)}")



    async def generate_query_param_from_profile(self, profile_text: str, max_terms: int = 8) -> Optional[str]:
        """
        Generate a concise search query string from profile text for Simpler.Grants API.

        Returns a string (5-100 chars per API spec) or raises exception if all attempts fail.
        """
        system_prompt = '''
            You are an expert at analyzing academic/research profiles and generating grant search queries.
            Generate a focused search query that will find relevant federal grant opportunities.
            Focus on: research area, field of study, expertise, or target funding areas.
            Use terms like: 'research', 'fellowship', 'education', 'STEM', specific fields, etc.
            Return ONLY the query text - no quotes, no explanations, no markup.
            example of query that we are using to find grants are like this :
            {
                "filters": {
                    "agency": {
                    "one_of": [
                        "USAID",
                        "DOC"
                    ]
                    },
                    "applicant_type": {
                    "one_of": [
                        "state_governments",
                        "county_governments",
                        "individuals"
                    ]
                    },
                    "close_date": {
                    "start_date": "2024-01-01"
                    },
                    "funding_category": {
                    "one_of": [
                        "recovery_act",
                        "arts",
                        "natural_resources"
                    ]
                    },
                    "funding_instrument": {
                    "one_of": [
                        "cooperative_agreement",
                        "grant"
                    ]
                    },
                    "opportunity_status": {
                    "one_of": [
                        "forecasted",
                        "posted"
                    ]
                    },
                    "post_date": {
                    "end_date": "2024-02-01",
                    "start_date": "2024-01-01"
                    }
                },
                "pagination": {
                    "page_offset": 1,
                    "page_size": 25,
                    "sort_order": [
                    {
                        "order_by": "opportunity_id",
                        "sort_direction": "ascending"
                    }
                    ]
                },
                "query": "research"
                }"
            )
    
                and you only need to generate the query part of above paylod like this : "research"
                ALSO, make sure the query length is between 1 and 50 characters.
             '''

        prompt = f"Profile:\n{profile_text}\n\nGenerate a relevant grant search query for this profile:" 
        logger = logging.getLogger(__name__)
        try:
            query = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=1000,
            )
            print("raw query is :", query)
            query = query.strip().strip('"').strip("'")
            print("generated query is :", query)


            if 1 <= len(query) <= 100:
                return query
            else:
                logger.warning(f"Generated query length out of bounds: '{query}' (length {len(query)})")
                return None
        except Exception as e:
            logger.error(f"Error generating query from profile: {e}")
            return None
       
        
    
    async def generate_email(
        self,
        profile_text: str,
        opportunity_text: str,
        fit_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate a cold email for an opportunity.
        
        Args:
            profile_text: User's profile
            opportunity_text: Opportunity description
            fit_analysis: Previous fit analysis
            
        Returns:
            Generated email text
        """
        system_prompt = """You are an expert at writing compelling cold emails for job/internship applications.
                            Write professional, personalized emails that highlight the candidate's relevant experience and fit.
                            Keep emails concise (200-300 words), engaging, and action-oriented."""

        prompt = f"""Write a cold email for this opportunity based on the candidate's profile.

                    CANDIDATE PROFILE:
                    {profile_text}

                    OPPORTUNITY:
                    {opportunity_text}

                    FIT ANALYSIS:
                    {json.dumps(fit_analysis, indent=2)}

                    Write a compelling cold email that:
                    1. Opens with a strong hook
                    2. Highlights 2-3 most relevant qualifications
                    3. Shows genuine interest and cultural fit
                    4. Includes a clear call to action
                    5. Maintains professional tone

                    Do not include subject line. Just the email body."""

        return await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
    
    async def generate_subject_line(
        self,
        profile_text: str,
        opportunity_text: str
    ) -> str:
        """Generate an email subject line."""
        system_prompt = """You are an expert at writing attention-grabbing email subject lines.
                            Create subject lines that are professional, specific, and highlight key qualifications.
                        """

        prompt = f"""Create a compelling subject line for a cold email application.

                    CANDIDATE PROFILE:
                    {profile_text}

                    OPPORTUNITY:
                    {opportunity_text}

                    Write ONE subject line (max 80 characters) that:
                    - Mentions the position/opportunity
                    - Includes candidate name or key qualification
                    - Creates interest without being clickbait

                    Just return the subject line text, nothing else.
                """

        return await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=100
        )
    
    async def generate_sop_paragraph(
        self,
        profile_text: str,
        opportunity_text: str,
        fit_analysis: Dict[str, Any]
    ) -> str:
        """Generate a statement of purpose paragraph."""
        system_prompt = """You are an expert at writing compelling SOP paragraphs for academic and professional applications.
                            Write focused paragraphs that connect the candidate's experience to the opportunity's goals.
                        """

        prompt = f"""Write a strong Statement of Purpose paragraph for this opportunity.

                    CANDIDATE PROFILE:
                    {profile_text}

                    OPPORTUNITY:
                    {opportunity_text}

                    FIT ANALYSIS:
                    {json.dumps(fit_analysis, indent=2)}

                    Write ONE well-structured paragraph (150-200 words) that:
                    1. Connects candidate's experience to opportunity
                    2. Demonstrates specific knowledge/interest in the organization
                    3. Highlights unique value proposition
                    4. Shows alignment with goals

                    Return only the paragraph text.
                """

        return await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=400
        )
    
    async def generate_fit_bullets(
        self,
        profile_text: str,
        opportunity_text: str,
        fit_analysis: Dict[str, Any]
    ) -> str:
        """Generate bullet points highlighting fit."""
        system_prompt = """You are an expert at writing impactful bullet points for resumes and applications.
                            Create bullets that are specific, quantified when possible, and directly address requirements.
                        """

        prompt = f"""Create bullet points highlighting the candidate's fit for this opportunity.

                    CANDIDATE PROFILE:
                    {profile_text}

                    OPPORTUNITY:
                    {opportunity_text}

                    FIT ANALYSIS:
                    {json.dumps(fit_analysis, indent=2)}

                    Write 4-5 bullet points that:
                    - Start with strong action verbs
                    - Include specific achievements and impacts
                    - Directly address key requirements
                    - Are concise and scannable

                    Return bullets in this format:
                    • First bullet point
                    • Second bullet point
                    etc.
                """

        return await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )


# Global LLM client instance
llm_client = LLMClient()
