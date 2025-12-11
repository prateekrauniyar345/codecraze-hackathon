"""
Service layer for LLM-powered features.
"""
import json
from typing import Dict, Any

from services.llm_client import llm_client
from schemas.profile import ProfileUpdate
from pydantic import ValidationError

class LLMService:
    """
    Service for handling all LLM-related business logic.
    """
    
    def __init__(self):
        self.llm_client = llm_client
    
    async def extract_profile_from_text(self, text: str) -> ProfileUpdate:
        """
        Extracts structured profile information from a given text using an LLM.

        Args:
            text: The text to extract information from (e.g., resume content).

        Returns:
            A ProfileUpdate schema object populated with the extracted data.
        """
        system_prompt = """You are an expert HR assistant specializing in parsing resumes. 
                            Your task is to extract structured information from the provided resume text and return it as a valid JSON object.
                            Follow these rules precisely:
                            1.  **Extract all possible information.** If a field is not present in the resume, omit it from the JSON output.
                            2.  **Format fields correctly:**
                                *   `full_name`: string
                                *   `email`: string (must be a valid email format)
                                *   `phone_number`: string
                                *   `linkedin_url`: string (must be a valid URL)
                                *   `github_url`: string (must be a valid URL)
                                *   `personal_website_url`: string (must be a valid URL)
                                *   `summary`: string (a professional summary or objective)
                                *   `skills`: array of strings
                                *   `education`: array of objects, each with `institution`, `degree`, `start_date`, `end_date`, and `gpa`.
                                *   `experience`: array of objects, each with `company`, `position`, `start_date`, `end_date`, and `responsibilities` (an array of strings).
                                *   `projects`: array of objects, each with `name`, `description`, and `technologies` (an array of strings).
                                *   `languages`: array of objects, each with `language` and `proficiency`.
                                *   `certifications`: array of objects, each with `name`, `issuing_organization`, and `date_issued`.
                                *   `awards`: array of objects, each with `name`, `issuing_organization`, and `date_awarded`.
                            3.  **Return only the JSON object.** Do not include any other text, comments, or explanations.
                        """
        
        prompt = f"""Please extract the profile information from the following text:

                    {text}
                    """
        
        try:
            response_text = await self.llm_client.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=3000,
                json_mode=True
            )
            
            print("\n=== RAW LLM RESPONSE TEXT ===")
            print(response_text)
            print("=== END RAW LLM RESPONSE ===\n")

            extracted_data = json.loads(response_text)

            print("\n=== PARSED JSON ===")
            print(extracted_data)
            print("=== END PARSED JSON ===\n")

            profile_update = ProfileUpdate(**extracted_data)
            return profile_update

        except json.JSONDecodeError as e:
            print("JSONDecodeError while parsing LLM response:", e)
            raise Exception(f"Failed to parse LLM JSON response: {str(e)}")
        except ValidationError as e:
            print("ValidationError in ProfileUpdate:", e)
            raise Exception(f"Profile extraction validation failed: {str(e)}")
        except Exception as e:
            print("Generic error in extract_profile_from_text:", e)
            raise Exception(f"Profile extraction failed: {str(e)}")

# Global LLM service instance
llm_service = LLMService()
