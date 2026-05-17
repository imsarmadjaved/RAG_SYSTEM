import json
from app.config import settings
from app.dependencies import get_ai
from loguru import logger

class QueryProcessor:
    def __init__(self):
        self.client = get_ai()
    
    async def process_query(self, query, email):
        try:
            resp = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", temperature=0, max_tokens=200,
                messages=[{"role":"system","content":"Analyze resume question. Return JSON: {\"intent\":\"skills|experience|education|summary|general\",\"reformulated_query\":\"\"}"},
                         {"role":"user","content":query}],
                response_format={"type":"json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
        except:
            data = {"intent":"general","reformulated_query":query}
        
        intent = data.get('intent', 'general')
        mapping = {
            'skills': ['skills', 'summary'],
            'experience': ['experience'],
            'education': ['education'],
            'summary': ['summary', 'experience', 'skills', 'education'],
            'general': ['summary', 'skills', 'experience', 'education']
        }
        
        return {
            'email': email,
            'intent': intent,
            'chunk_types': mapping.get(intent, ['summary', 'skills', 'experience']),
            'query_text': data.get('reformulated_query', query),
            'original_query': query
        }
