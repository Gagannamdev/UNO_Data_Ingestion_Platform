from app.constants.messages import ErrorMessages
from app.enums.role_enum import UserRole
from app.exceptions.custom_exceptions import (
    ConflictException,
    NotFoundException,
)
from app.repositories.user_repository import UserRepository
from app.schema.models.user_model import create_user_document
from app.utils.security import hash_password


class UserService:

    @staticmethod
    def format_user(user: dict) -> dict:
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
        }

    @staticmethod
    async def create_data_engineer(
        name: str,
        email: str,
        password: str,
    ) -> dict:

        existing_user = await UserRepository.find_by_email(email)

        if existing_user:
            raise ConflictException(
                ErrorMessages.EMAIL_ALREADY_EXISTS,
                error_code="EMAIL_ALREADY_EXISTS",
            )

        user_document = create_user_document(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.DATA_ENGINEER,
        )

        user = await UserRepository.create(user_document)

        return UserService.format_user(user)

    @staticmethod
    async def get_all_users() -> list[dict]:
        users = await UserRepository.find_all()

        return [
            UserService.format_user(user)
            for user in users
        ]

    @staticmethod
    async def get_user_by_id(user_id: str) -> dict:
        user = await UserRepository.find_by_id(user_id)

        if not user:
            raise NotFoundException(
                ErrorMessages.USER_NOT_FOUND,
                error_code="USER_NOT_FOUND",
            )

        return UserService.format_user(user)
