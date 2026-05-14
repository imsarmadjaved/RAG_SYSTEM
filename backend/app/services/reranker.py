import json
from app.config import settings
from app.dependencies import get_oai
from loguru import logger

class Reranker:
    def __init__(self):
        self.client = get_oai()
    
    async def rerank(self, query, chunks, top_n=5):
        if len(chunks) <= top_n: return chunks
        
        try:
            items = [f"{i}: [{c.get('chunk_type','')}] {c.get('text','')[:150]}" for i, c in enumerate(chunks)]
            resp = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", temperature=0, max_tokens=150,
                messages=[{"role":"system","content":"Rank results. Return JSON: {\"ranked_indices\":[]}"},
                         {"role":"user","content":f"Query: {query}\n\n" + "\n".join(items)}],
                response_format={"type":"json_object"}
            )
            ranked = json.loads(resp.choices[0].message.content).get('ranked_indices', [])
            
            result = []
            for i in ranked:
                if i < len(chunks):
                    chunks[i]['rerank_score'] = 10 - ranked.index(i)
                    result.append(chunks[i])
            for i, c in enumerate(chunks):
                if i not in ranked: result.append(c)
            return result[:top_n]
        except:
            return chunks[:top_n]
