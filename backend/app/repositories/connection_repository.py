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


class ConnectionRepository:

    @staticmethod
    async def create(connection: dict):
        try:
            database = get_database()

            result = await database.connections.insert_one(
                connection
            )

            return await database.connections.find_one({
                "_id": result.inserted_id
            })

        except DuplicateKeyError as exc:
            raise ConflictException(
                ErrorMessages.CONNECTION_NAME_EXISTS,
                error_code="CONNECTION_NAME_EXISTS",
            ) from exc

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def find_by_id(connection_id: str):
        try:
            if not ObjectId.is_valid(connection_id):
                return None

            database = get_database()

            return await database.connections.find_one({
                "_id": ObjectId(connection_id)
            })

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def find_all(owner_id: str | None = None):
        try:
            database = get_database()

            query = {}

            if owner_id:
                query["owner_id"] = owner_id

            return await database.connections.find(
                query
            ).sort(
                "created_at",
                -1,
            ).to_list(length=200)

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def update(
        connection_id: str,
        updates: dict,
    ):
        try:
            database = get_database()

            await database.connections.update_one(
                {"_id": ObjectId(connection_id)},
                {"$set": updates},
            )

            return await database.connections.find_one({
                "_id": ObjectId(connection_id)
            })

        except DuplicateKeyError as exc:
            raise ConflictException(
                ErrorMessages.CONNECTION_NAME_EXISTS,
                error_code="CONNECTION_NAME_EXISTS",
            ) from exc

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def update_status(
        connection_id: str,
        status: str,
    ):
        try:
            database = get_database()

            await database.connections.update_one(
                {
                    "_id": ObjectId(connection_id)
                },
                {
                    "$set": {
                        "status": status
                    }
                },
            )

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def delete(connection_id: str):
        try:
            database = get_database()

            return await database.connections.delete_one({
                "_id": ObjectId(connection_id)
            })

        except PyMongoError as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc
