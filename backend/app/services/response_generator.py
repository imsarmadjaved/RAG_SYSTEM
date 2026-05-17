from app.config import settings
from app.dependencies import get_ai
from loguru import logger

class ResponseGenerator:
    def __init__(self):
        self.client = get_ai()
    
    async def generate(self, query, context_chunks, chat_history=None):
        ctx = "\n\n".join([f"[{c.get('chunk_type','').upper()}] {c.get('text','')}" for c in context_chunks if c.get('text')])
        
        history_text = ""
        if chat_history and len(chat_history) > 0:
            parts = [f"{'User' if m.get('role')=='user' else 'Assistant'}: {str(m.get('content',''))[:200]}" for m in chat_history[-4:]]
            history_text = "\n".join(parts)
        
        prompt = f"""You are a helpful resume assistant. Answer naturally. Use resume data when available. For career questions, give general advice. Only refuse completely unrelated topics.

Resume:\n{ctx}\n\n{f'History:\n{history_text}\n\n' if history_text else ''}Q: {query}\nA:"""
        
        try:
            resp = self.client.models.generate_content(model=settings.OPENAI_MODEL_CHAT, contents=prompt)
            answer = resp.text
            
            used = sum(1 for c in context_chunks if c.get('text','') and len(c.get('text',''))>20 and len(set(c.get('text','').lower().split()[:12]) & set(answer.lower().split())) >= 2)
            ratio = used / max(len(context_chunks), 1)
            conf = "high" if ratio > 0.6 else ("medium" if ratio > 0.3 else "low")
            
            sources = [{'chunk_id': c.get('id',''), 'chunk_text': c.get('text','')[:200], 'chunk_type': c.get('chunk_type',''), 'relevance_score': c.get('rerank_score', c.get('score',0))} for c in context_chunks[:5]]
            
            return {'answer': answer, 'confidence_score': round(ratio*100,1), 'confidence_level': conf, 'sources': sources}
        except Exception as e:
            logger.error(f"Generate error: {e}")
            return {'answer': "Error generating response.", 'confidence_score': 0, 'confidence_level': 'low', 'sources': []}
