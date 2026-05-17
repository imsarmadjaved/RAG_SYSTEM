class ScoringEngine:
    def calculate_score(self, candidate, requirements):
        req_skills = [s.lower().strip() for s in requirements.get('required_skills', [])]
        min_exp = requirements.get('min_experience_years', 0)
        cand_skills = [s.lower().strip() for s in candidate.get('skills', [])]
        
        # Skill match (70% weight - most important)
        if req_skills:
            matched = 0
            for req in req_skills:
                for cand in cand_skills:
                    if req == cand or req in cand or cand in req:
                        matched += 1
                        break
            skill_score = (matched / len(req_skills)) * 70
            skills_matched = [s for s in req_skills if any(s == c or s in c or c in s for c in cand_skills)]
            skills_missing = [s for s in req_skills if s not in skills_matched]
        else:
            skill_score = 40
            skills_matched = cand_skills[:5]
            skills_missing = []
        
        # Experience (20%)
        exp = candidate.get('total_exp', 0)
        if min_exp > 0:
            exp_score = min(exp / max(min_exp, 1), 1) * 20
        else:
            exp_score = 15 if exp > 0 else 5
        
        # Semantic relevance (10%)
        rel = min(candidate.get('avg_score', 0), 1.0) * 10
        
        total = min(skill_score + exp_score + rel, 100)
        
        return {
            'match_score': round(total, 1),
            'skills_matched': skills_matched,
            'skills_missing': skills_missing,
            'experience_years': exp
        }
