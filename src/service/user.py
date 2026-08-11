from src.database import Database 
from src.models.user import UserResponse , UserReuest ,LoginRequest
from cryptography.fernet import Fernet
from src.security import security
from src.jwt_handler import jwt_handler 
from fastapi import HTTPException, status

db = Database()

class UserService:
    async def create_user(self, request : UserReuest):
        user_request = request.model_dump()
        user = await db.create_user(user_request)
        print(Fernet.generate_key().decode()) 
        return {
            "id" :user["_id"],
            "name": user["name"],
            "email": user["email"]
        }

    async def get_user(self,id:str):
        result = await db.get_user(id)
        return result

    async def login(self, request :LoginRequest):
        result = await db.login(request.email)

        if result is None:
           raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        if security.verify_password(request.password ,result["password"]):
          
            access = jwt_handler.create_access_token(
                result["email"]
            )
            refresh = jwt_handler.create_refresh_token(result["email"])
            return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "Bearer"
             }
        else:
           raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid  password"
            )
            
user_service = UserService()