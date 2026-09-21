from bson import ObjectId
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)

from app.constants.messages import ErrorMessages
from app.exceptions.custom_exceptions import (
    ConflictException,
    DatabaseException,
)
from database import get_database


class UserRepository:

    @staticmethod
    async def find_by_email(email: str):
        try:
            database = get_database()

            return await database.users.find_one({
                "email": email.lower()
            })

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def find_by_id(user_id: str):
        try:
            if not ObjectId.is_valid(user_id):
                return None

            database = get_database()

            return await database.users.find_one({
                "_id": ObjectId(user_id)
            })

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def create(user: dict):
        try:
            database = get_database()

            result = await database.users.insert_one(user)

            return await database.users.find_one({
                "_id": result.inserted_id
            })

        except DuplicateKeyError as exc:
            raise ConflictException(
                ErrorMessages.EMAIL_ALREADY_EXISTS,
                error_code="EMAIL_ALREADY_EXISTS",
            ) from exc

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def find_all():
        try:
            database = get_database()

            return await database.users.find(
                {},
                {"password_hash": 0},
            ).sort(
                "created_at",
                -1,
            ).to_list(length=100)

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc
