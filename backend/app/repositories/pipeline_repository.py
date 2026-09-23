from datetime import datetime

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.constants.messages import ErrorMessages
from app.exceptions.custom_exceptions import (
    ConflictException,
    DatabaseException,
)
from database import get_database


class PipelineRepository:

    @staticmethod
    async def create(pipeline: dict) -> dict:
        try:
            database = get_database()

            result = await database.pipelines.insert_one(
                pipeline
            )

            pipeline["_id"] = result.inserted_id

            return pipeline

        except DuplicateKeyError as exc:
            raise ConflictException(
                ErrorMessages.PIPELINE_NAME_EXISTS,
                error_code="PIPELINE_NAME_EXISTS",
            ) from exc

        except Exception as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def find_all(
        owner_id: str | None = None,
    ) -> list[dict]:
        try:
            database = get_database()

            query = {}

            if owner_id:
                query["owner_id"] = owner_id

            cursor = database.pipelines.find(query).sort(
                "created_at",
                -1,
            )

            return await cursor.to_list(length=None)

        except Exception as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def find_by_id(
        pipeline_id: str,
    ) -> dict | None:
        try:
            database = get_database()

            if not ObjectId.is_valid(pipeline_id):
                return None

            return await database.pipelines.find_one(
                {"_id": ObjectId(pipeline_id)}
            )

        except Exception as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def update(
        pipeline_id: str,
        updates: dict,
    ) -> dict:
        try:
            database = get_database()

            result = await database.pipelines.find_one_and_update(
                {"_id": ObjectId(pipeline_id)},
                {
                    "$set": updates,
                },
                return_document=True,
            )

            if result is None:
                return None

            return result

        except DuplicateKeyError as exc:
            raise ConflictException(
                ErrorMessages.PIPELINE_NAME_EXISTS,
                error_code="PIPELINE_NAME_EXISTS",
            ) from exc

        except Exception as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc

    @staticmethod
    async def delete(
        pipeline_id: str,
    ) -> bool:
        try:
            database = get_database()

            result = await database.pipelines.delete_one(
                {"_id": ObjectId(pipeline_id)}
            )

            return result.deleted_count > 0

        except Exception as exc:
            raise DatabaseException(
                ErrorMessages.DATABASE_OPERATION_FAILED
            ) from exc
