from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.models.search import RecruiterSearchQuery, CandidateResult, SearchResponse
from app.services.requirement_extractor import RequirementExtractor
from app.services.recruiter_search import RecruiterSearchService
from app.services.scoring_engine import ScoringEngine
from app.dependencies import get_db
from app.utils.auth_utils import get_current_active_user
from app.utils.helpers import generate_uuid
from loguru import logger

router = APIRouter()

@router.post("/search")
async def search(data: RecruiterSearchQuery, user=Depends(get_current_active_user)):
    try:
        db = get_db()
        ext = RequirementExtractor()
        search_svc = RecruiterSearchService()
        scorer = ScoringEngine()
        
        reqs = await ext.extract_requirements(data.query)
        if data.required_skills: reqs['required_skills'] = data.required_skills
        if data.min_experience: reqs['min_experience_years'] = data.min_experience
        
        candidates = await search_svc.search(
            query_text=reqs.get('normalized_query', data.query),
            required_skills=reqs.get('required_skills', []),
            min_experience=reqs.get('min_experience_years', 0)
        )
        
        results = []
        for c in candidates:
            scores = scorer.calculate_score(c, reqs)
            
            edu = c.get('education', ['Not specified'])
            exp_list = c.get('experience', [])
            skills = c.get('skills', [])
            
            exp_text = exp_list[0] if exp_list else str(c.get('total_exp', 0)) + 'y exp'
            summary = exp_text + ". Skills: " + ', '.join(skills[:8])
            
            results.append(CandidateResult(
                user_id=c.get('email', ''), email=c['email'], match_score=scores['match_score'],
                skills_matched=scores['skills_matched'], skills_missing=scores['skills_missing'],
                experience_years=c.get('total_exp', 0), education=edu[0] if edu else 'Not specified',
                summary=summary
            ))
        
        results.sort(key=lambda x: x.match_score, reverse=True)
        
        try:
            await db.recruiter_searches.insert_one({
                "search_id": generate_uuid(), "recruiter_id": user["user_id"],
                "query": data.query, "result_count": len(results), "created_at": datetime.utcnow()
            })
        except: pass
        
        return SearchResponse(results=results[:20], total_results=len(results), page=1,
                              total_pages=max(len(results)//20, 1) if results else 1, query_analysis=reqs)
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(500, str(e))
