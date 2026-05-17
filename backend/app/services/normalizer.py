import json, asyncio
from app.config import settings
from app.dependencies import get_ai
from loguru import logger

class Normalizer:
    def __init__(self):
        self.client = get_ai()
    
    async def normalize_chunks(self, chunks):
        tasks = [self._normalize(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        normalized = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                logger.error(f"Chunk {i} failed: {r}")
                chunks[i]['extracted_data'] = {}
                chunks[i]['normalized_text'] = chunks[i].get('text', '')
                normalized.append(chunks[i])
            else:
                normalized.append(r)
        return normalized
    
    async def _normalize(self, chunk):
        text = chunk['text'][:2000]
        ctype = chunk['chunk_type']
        
        prompt = f"""Extract data from this resume [{ctype}] section. Return ONLY valid JSON.
For SKILLS: Extract each individual skill. Skip category headers.
For EXPERIENCE: Calculate total years from dates.
For EDUCATION: Extract degree, institution, year.
Text: {text}"""
        
        try:
            resp = self.client.models.generate_content(
                model=settings.OPENAI_MODEL_EXTRACTION,
                contents=prompt
            )
            raw = resp.text.strip()
            if raw.startswith("```json"): raw = raw[7:]
            if raw.endswith("```"): raw = raw[:-3]
            data = json.loads(raw)
            
            if data.get('skills'):
                data['skills'] = [s.strip() for s in data['skills'] if s and len(s.strip()) > 1]
            
            chunk['extracted_data'] = data
            chunk['normalized_text'] = self._format(data, ctype)
            return chunk
        except Exception as e:
            logger.error(f"Normalize error: {e}")
            chunk['extracted_data'] = {}
            chunk['normalized_text'] = text
            return chunk
    
    def _format(self, data, ctype):
        parts = []
        if data.get('skills'): parts.append("Skills: " + ', '.join(data['skills']))
        if data.get('experience'):
            for exp in data['experience']:
                if isinstance(exp, dict): parts.append(f"{exp.get('title','')} at {exp.get('company','')}")
        if data.get('education'):
            for edu in data['education']:
                if isinstance(edu, dict): parts.append(f"{edu.get('degree','')} - {edu.get('institution','')}")
        return '\n'.join(parts) if parts else 'Resume content'
