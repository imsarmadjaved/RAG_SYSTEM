import json, asyncio
from app.config import settings
from app.dependencies import get_oai
from loguru import logger

class Normalizer:
    def __init__(self):
        self.client = get_oai()
    
    async def normalize_chunks(self, chunks):
        tasks = [self._normalize(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        normalized = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                chunks[i]['extracted_data'] = {}
                chunks[i]['normalized_text'] = chunks[i].get('text', '')
                normalized.append(chunks[i])
            else:
                normalized.append(r)
        return normalized
    
    async def _normalize(self, chunk):
        text = chunk['text'][:2000]
        ctype = chunk['chunk_type']
        
        prompt = f"""Extract data from this resume [{ctype}] section.

For SKILLS: Extract each individual skill as written. Skip category headers (Frontend, Backend, etc).
For EXPERIENCE: Calculate total years from dates.
For EDUCATION: Extract degree, institution, year.

Text: {text}

Return JSON with relevant fields."""
        
        try:
            resp = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_EXTRACTION, temperature=0, max_tokens=500,
                messages=[{"role":"system","content":"Extract resume data. Keep skills as written. Return JSON."}, {"role":"user","content":prompt}],
                response_format={"type":"json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
            
            if data.get('skills'):
                data['skills'] = [s.strip() for s in data['skills'] if s and len(s.strip()) > 1 and not s.strip().endswith(':')]
            
            chunk['extracted_data'] = data
            chunk['normalized_text'] = self._format(data, ctype)
            return chunk
        except:
            chunk['extracted_data'] = {}
            chunk['normalized_text'] = text
            return chunk
    
    def _format(self, data, ctype):
        parts = []
        if data.get('skills'):
            parts.append("Skills: " + ', '.join(data['skills']))
        if data.get('experience'):
            for exp in data['experience']:
                if isinstance(exp, dict):
                    parts.append(f"{exp.get('title','')} at {exp.get('company','')} ({exp.get('duration_years',0)}y)")
        if data.get('education'):
            for edu in data['education']:
                if isinstance(edu, dict):
                    parts.append(f"{edu.get('degree','')} - {edu.get('institution','')}")
        return '\n'.join(parts) if parts else 'Resume content'
