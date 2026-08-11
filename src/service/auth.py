from fastapi import HTTPException, status

from src.jwt_handler import jwt_handler


class AuthService:

    async def refresh_token(self, request):

        payload = jwt_handler.verify_token(request.refresh_token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Refresh Token"
            )

        if payload["type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token Type"
            )

        access_token = jwt_handler.create_access_token(
            payload["sub"]
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

auth_service = AuthService()