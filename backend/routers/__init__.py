"""
Router package initialization.
"""
from . import auth, documents, profiles, opportunities, materials, llm_health_check, grants, jobs

__all__ = [
    "auth", 
    "documents", 
    "profiles", 
    "opportunities", 
    "materials",
    "llm_health_check", 
    "grants",
    "jobs",
    ]
