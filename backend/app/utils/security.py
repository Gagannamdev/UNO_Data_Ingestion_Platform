from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.constants.messages import ErrorMessages
from app.exceptions.custom_exceptions import (
    ForbiddenException,
    UnauthorizedException,
)
from configs.config import settings

security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def create_access_token(
    user_id: str,
    role: str,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "role": role,
        "iss": settings.app_name,
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.jwt_expire_minutes
        ),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.app_name,
        )

    except jwt.PyJWTError as exc:
        raise UnauthorizedException(
            ErrorMessages.INVALID_TOKEN,
            error_code="INVALID_TOKEN",
        ) from exc


def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    return decode_access_token(credentials.credentials)


def require_admin(
    payload: dict = Depends(get_token_payload),
) -> dict:
    if payload.get("role") != "admin":
        raise ForbiddenException(
            ErrorMessages.FORBIDDEN
        )

    return payload
