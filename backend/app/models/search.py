from pydantic import BaseModel
from typing import Optional, List

class RecruiterSearchQuery(BaseModel):
    query: str
    required_skills: Optional[List[str]] = []
    min_experience: Optional[int] = 0

class CandidateResult(BaseModel):
    user_id: str
    email: str
    match_score: float
    skills_matched: List[str] = []
    skills_missing: List[str] = []
    experience_years: float = 0
    education: str = ""
    summary: str = ""

class SearchResponse(BaseModel):
    results: List[CandidateResult]
    total_results: int
    page: int = 1
    total_pages: int = 1
    query_analysis: dict = {}
