from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from src.jwt_handler import jwt_handler

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    payload = jwt_handler.verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    if payload["type"] != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid Token Type"
        )

    return payload