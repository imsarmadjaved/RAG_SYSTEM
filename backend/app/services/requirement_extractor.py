import json
from app.config import settings
from app.dependencies import get_ai
from loguru import logger

class RequirementExtractor:
    def __init__(self):
        self.client = get_ai()
    
    async def extract_requirements(self, query):
        try:
            resp = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", temperature=0, max_tokens=300,
                messages=[{"role":"system","content":"Extract hiring requirements. Return JSON: {\"required_skills\":[],\"preferred_skills\":[],\"min_experience_years\":0,\"education_level\":\"\",\"normalized_query\":\"\"}"},
                         {"role":"user","content":query}],
                response_format={"type":"json_object"}
            )
            return json.loads(resp.choices[0].message.content)
        except:
            return {"required_skills":[], "preferred_skills":[], "min_experience_years":0, "normalized_query":query}
