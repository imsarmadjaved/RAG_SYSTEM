from datetime import datetime
from bson import ObjectId
from app.models.user import UserResponse, TokenResponse
from app.utils.auth_utils import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.errors import AppError, ErrorCode

class AuthService:
    def __init__(self, db):
        self.db = db
        self.users = db.users
    
    def _user_response(self, doc):
        return UserResponse(
            id=str(doc["_id"]), email=doc.get("email",""), full_name=doc.get("full_name",""),
            user_type=doc.get("user_type","candidate"), company=doc.get("company"),
            is_active=doc.get("is_active",True), created_at=doc.get("created_at")
        )
    
    async def signup(self, data):
        if await self.users.find_one({"email": data.email}):
            raise AppError(ErrorCode.AUTH_004, "Email already exists")
        
        doc = {"email": data.email, "full_name": data.full_name,
               "password_hash": hash_password(data.password),
               "user_type": data.user_type.value, "is_active": True,
               "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(),
               "refresh_token": None}
        if data.company: doc["company"] = data.company
        
        result = await self.users.insert_one(doc)
        user_id = str(result.inserted_id)
        
        token_data = {"sub": user_id, "email": data.email, "user_type": doc["user_type"]}
        access = create_access_token(token_data)
        refresh = create_refresh_token(token_data)
        await self.users.update_one({"_id": result.inserted_id}, {"$set": {"refresh_token": refresh}})
        
        created = await self.users.find_one({"_id": result.inserted_id})
        return TokenResponse(access_token=access, refresh_token=refresh, user=self._user_response(created))
    
    async def login(self, data):
        user = await self.users.find_one({"email": data.email})
        if not user or not verify_password(data.password, user["password_hash"]):
            raise AppError(ErrorCode.AUTH_001, "Invalid credentials")
        
        user_id = str(user["_id"])
        token_data = {"sub": user_id, "email": user["email"], "user_type": user["user_type"]}
        access = create_access_token(token_data)
        refresh = create_refresh_token(token_data)
        await self.users.update_one({"_id": user["_id"]}, {"$set": {"refresh_token": refresh, "updated_at": datetime.utcnow()}})
        
        updated = await self.users.find_one({"_id": user["_id"]})
        return TokenResponse(access_token=access, refresh_token=refresh, user=self._user_response(updated))
    
    async def logout(self, user_id):
        oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
        await self.users.update_one({"_id": oid}, {"$set": {"refresh_token": None}})
        return {"message": "Logged out"}
    
    async def get_profile(self, user_id):
        oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
        user = await self.users.find_one({"_id": oid})
        if not user: raise AppError(ErrorCode.AUTH_001, "User not found", 404)
        return self._user_response(user)
