from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from src.settings import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)


class JWTHandler:

    def create_access_token(self, email: str):

        payload = {
            "sub": email,
            "type": "access",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

    def create_refresh_token(self, email: str):

        payload = {
            "sub": email,
            "type": "refresh",
            "exp": datetime.now(timezone.utc)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

    def verify_token(self, token: str):

        try:

            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            return payload

        except JWTError:

            return None


jwt_handler = JWTHandler()