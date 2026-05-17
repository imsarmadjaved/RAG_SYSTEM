from datetime import datetime
from app.utils.helpers import generate_session_id
from app.services.query_processor import QueryProcessor
from app.services.search_service import SearchService
from app.services.reranker import Reranker
from app.services.response_generator import ResponseGenerator
from loguru import logger

class ChatManager:
    def __init__(self, db):
        self.db = db
        self.chats = db.chat_history
        self.docs = db.documents
        self.qp = QueryProcessor()
        self.search = SearchService()
        self.reranker = Reranker()
        self.gen = ResponseGenerator()
    
    async def chat(self, query, email, user_id, session_id=None):
        if not session_id:
            session_id = generate_session_id()
        
        # Check if user has resume
        count = await self.docs.count_documents({"user_id": user_id, "status": "completed"})
        if count == 0:
            return {'answer': "Please upload your resume first from the Dashboard.", 'confidence_score': 0, 'confidence_level': 'low', 'sources': [], 'session_id': session_id}
        
        history = await self._history(session_id)
        params = await self.qp.process_query(query, email)
        chunks = await self.search.search(params['query_text'], email, params.get('chunk_types'))
        
        if not chunks:
            resp = {'answer': "I couldn't find that in your resume. Try asking about skills, experience, or education.", 'confidence_score': 0, 'confidence_level': 'low', 'sources': []}
        else:
            top = await self.reranker.rerank(query, chunks)
            resp = await self.gen.generate(query, top, history)
        
        await self._save(session_id, user_id, email, 'user', query)
        await self._save(session_id, user_id, email, 'assistant', resp['answer'])
        resp['session_id'] = session_id
        return resp
    
    async def _history(self, sid):
        s = await self.chats.find_one({"session_id": sid})
        return s.get('messages', []) if s else []
    
    async def _save(self, sid, uid, email, role, content):
        try:
            msg = {"role": role, "content": content, "timestamp": datetime.utcnow()}
            r = await self.chats.update_one({"session_id": sid}, {"$set": {"messages": msg}})
            if r.matched_count == 0:
                await self.chats.insert_one({"session_id": sid, "user_id": uid, "email": email, "messages": [msg], "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()})
        except: pass
    
    async def get_history(self, sid):
        s = await self.chats.find_one({"session_id": sid})
        return {"session_id": sid, "messages": s.get('messages',[]), "total_messages": len(s.get('messages',[]))} if s else {"session_id": sid, "messages": [], "total_messages": 0}
    
    async def get_sessions(self, uid):
        sessions = []
        async for s in self.chats.find({"user_id": uid}).sort("updated_at", -1).limit(20):
            last = s['messages'][-1]['content'][:50] if s.get('messages') else ''
            sessions.append({"session_id": s['session_id'], "last_message": last, "updated_at": str(s.get('updated_at',''))})
        return sessions
