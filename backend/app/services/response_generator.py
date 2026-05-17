import google.generativeai as genai
from app.config import settings
from loguru import logger

class ResponseGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.OPENAI_MODEL_CHAT)
    
    async def generate(self, query, context_chunks, chat_history=None):
        ctx = "\n\n".join([f"[{c.get('chunk_type','').upper()}] {c.get('text','')}" for c in context_chunks if c.get('text')])
        
        history_text = ""
        if chat_history and len(chat_history) > 0:
            parts = []
            for m in chat_history[-4:]:
                role = "User" if m.get("role") == "user" else "Assistant"
                parts.append(f"{role}: {str(m.get('content',''))[:200]}")
            history_text = "\n".join(parts)
        
        prompt = f"""You are a resume assistant. Answer naturally using resume data when available. For career questions, give general advice.

Resume:
{ctx}

{f'Chat History:\n{history_text}\n\n' if history_text else ''}
Q: {query}
A:"""
        
        try:
            resp = self.model.generate_content(prompt)
            answer = resp.text
            
            used = 0
            answer_lower = answer.lower()
            for c in context_chunks:
                text = c.get('text','')
                if text and len(text) > 20:
                    words = set(text.lower().split()[:12])
                    if sum(1 for w in words if w in answer_lower) >= 2: used += 1
            
            ratio = used / max(len(context_chunks), 1)
            conf = "high" if ratio > 0.6 else ("medium" if ratio > 0.3 else "low")
            
            sources = [{'chunk_id': c.get('id',''), 'chunk_text': c.get('text','')[:200],
                        'chunk_type': c.get('chunk_type',''), 'relevance_score': c.get('rerank_score', c.get('score',0))}
                       for c in context_chunks[:5]]
            
            return {'answer': answer, 'confidence_score': round(ratio*100,1), 'confidence_level': conf, 'sources': sources}
        except Exception as e:
            logger.error(f"Generate error: {e}")
            return {'answer': "Error generating response.", 'confidence_score': 0, 'confidence_level': 'low', 'sources': []}
