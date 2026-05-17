ï»¿from app.config import settings
from app.dependencies import get_ai, get_pc
from loguru import logger

class RecruiterSearchService:
    def __init__(self):
        self.ai = get_ai()
        self.index = get_pc().Index(settings.PINECONE_INDEX_CHUNKS)
    
    async def search(self, query_text, required_skills=None, min_experience=0, top_k=50):
        try:
            emb = await self.ai.embeddings.create(model=settings.OPENAI_MODEL_EMBEDDING, input=query_text)
            vec = emb.data[0].embedding
            
            # Get more results for better coverage
            results = self.index.query(vector=vec, top_k=top_k, include_metadata=True)
            
            candidates = {}
            for m in results.matches:
                meta = m.metadata
                email = meta.get('email', '')
                if not email or email == 'None': continue
                
                if email not in candidates:
                    candidates[email] = {
                        'email': email, 'skills': [], 'experience': [], 'education': [],
                        'chunks': [], 'total_score': 0, 'chunk_count': 0, 'total_exp': 0
                    }
                
                c = candidates[email]
                text = meta.get('normalized_text', meta.get('raw_text', ''))
                ctype = meta.get('chunk_type', '')
                c['chunks'].append({'text': text, 'type': ctype, 'score': m.score})
                c['total_score'] += m.score
                c['chunk_count'] += 1
                
                # Collect skills WITHOUT normalizing - keep as-is
                for s in meta.get('skills', []):
                    if s and isinstance(s, str) and len(s) > 1 and s not in c['skills']:
                        c['skills'].append(s)
                
                if ctype == 'experience':
                    c['experience'].append(text)
                elif ctype == 'education':
                    c['education'].append(text)
                
                exp = meta.get('experience_years', 0)
                if isinstance(exp, (int, float)) and exp > c['total_exp']:
                    c['total_exp'] = exp
            
            result = []
            for email, data in candidates.items():
                data['avg_score'] = data['total_score'] / max(data['chunk_count'], 1)
                
                # Flexible skill matching
                if required_skills and len(required_skills) > 0:
                    if not self._skill_match(data['skills'], required_skills):
                        continue
                
                if min_experience > 0 and data['total_exp'] < min_experience:
                    continue
                
                result.append(data)
            
            result.sort(key=lambda x: x['avg_score'], reverse=True)
            logger.info(f"Found {len(result)} candidates")
            return result
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _skill_match(self, candidate_skills, required_skills):
        """Flexible matching - case insensitive, partial, and semantic"""
        if not required_skills:
            return True
        
        cand_lower = [s.lower().strip() for s in candidate_skills]
        req_lower = [s.lower().strip() for s in required_skills]
        
        # Check each required skill
        for req in req_lower:
            matched = False
            for cand in cand_lower:
                # Exact match
                if req == cand:
                    matched = True
                    break
                # Substring match (react in react.js, node in node.js)
                if req in cand or cand in req:
                    matched = True
                    break
                # Common variations
                if req == 'react' and cand in ['react.js', 'reactjs']:
                    matched = True
                    break
                if req == 'node' and cand in ['node.js', 'nodejs']:
                    matched = True
                    break
            
            if not matched:
                return False
        
        return True
