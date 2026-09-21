from app.constants.messages import ErrorMessages
from app.exceptions.custom_exceptions import UnauthorizedException
from app.repositories.user_repository import UserRepository
from app.utils.security import (
    create_access_token,
    verify_password,
)


class AuthService:

    @staticmethod
    async def login(
        email: str,
        password: str,
    ) -> dict:

        user = await UserRepository.find_by_email(email)

        if not user:
            raise UnauthorizedException(
                ErrorMessages.INVALID_CREDENTIALS,
                error_code="INVALID_CREDENTIALS",
            )

        if not user.get("is_active", True):
            raise UnauthorizedException(
                ErrorMessages.INVALID_CREDENTIALS,
                error_code="INVALID_CREDENTIALS",
            )

        if not verify_password(
            password,
            user["password_hash"],
        ):
            raise UnauthorizedException(
                ErrorMessages.INVALID_CREDENTIALS,
                error_code="INVALID_CREDENTIALS",
            )

        token = create_access_token(
            user_id=str(user["_id"]),
            role=user["role"],
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }
