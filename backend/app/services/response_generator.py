from app.config import settings
from app.dependencies import get_ai
from loguru import logger

class ResponseGenerator:
    def __init__(self):
        self.client = get_ai()
    
    async def generate(self, query, context_chunks, chat_history=None):
        ctx_parts = []
        for c in context_chunks:
            if c.get("text"):
                ctx_parts.append("[" + c.get("chunk_type","").upper() + "] " + c.get("text",""))
        ctx = "\n\n".join(ctx_parts)
        
        history_text = ""
        if chat_history and len(chat_history) > 0:
            parts = []
            if isinstance(chat_history, list):
                for m in chat_history[-4:]:
                    role = "User" if m.get("role") == "user" else "Assistant"
                    parts.append(role + ": " + str(m.get("content",""))[:100])
                history_text = "\n".join(parts)
        
        prompt = "You are a helpful resume assistant.\n\nResume:\n" + ctx
        if history_text:
            prompt += "\n\nHistory:\n" + history_text
        prompt += "\n\nQ: " + query + "\nA:"
        
        try:
            resp = self.client.models.generate_content(
                model=settings.OPENAI_MODEL_CHAT,
                contents=prompt
            )
            answer = resp.text
            
            used = 0
            for c in context_chunks:
                text = c.get("text","")
                if text and len(text) > 20:
                    words = set(text.lower().split()[:12])
                    if len(words & set(answer.lower().split())) >= 2:
                        used += 1
            
            ratio = used / max(len(context_chunks), 1)
            conf = "high" if ratio > 0.6 else ("medium" if ratio > 0.3 else "low")
            
            sources = []
            for c in context_chunks[:5]:
                sources.append({
                    "chunk_id": c.get("id",""),
                    "chunk_text": c.get("text","")[:200],
                    "chunk_type": c.get("chunk_type",""),
                    "relevance_score": c.get("rerank_score", c.get("score",0))
                })
            
            return {"answer": answer, "confidence_score": round(ratio*100,1), "confidence_level": conf, "sources": sources}
        except Exception as e:
            logger.error("Generate error: " + type(e).__name__ + " - " + str(e))
            return {"answer": "Error: " + type(e).__name__ + " - " + str(e)[:200], "confidence_score": 0, "confidence_level": "low", "sources": []}