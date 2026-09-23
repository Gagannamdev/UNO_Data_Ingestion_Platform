from typing import Any, Awaitable, Callable

from motor.motor_asyncio import AsyncIOMotorClient

from app.constants.messages import (
    ErrorMessages,
    SuccessMessages,
)
from app.exceptions.custom_exceptions import DatabaseException
from configs.config import settings


class MongoDB:
    client: AsyncIOMotorClient | None = None
    database = None


mongodb = MongoDB()


async def connect_to_mongodb() -> None:
    try:
        mongodb.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
        )

        await mongodb.client.admin.command("ping")

        mongodb.database = mongodb.client[
            settings.mongodb_database
        ]

        await create_indexes()

        print(SuccessMessages.DATABASE_CONNECTED)

    except Exception as exc:
        mongodb.client = None
        mongodb.database = None

        print(
            f"{ErrorMessages.DATABASE_CONNECTION_FAILED}: {exc}"
        )

        raise DatabaseException(
            ErrorMessages.DATABASE_CONNECTION_FAILED
        ) from exc


async def create_indexes() -> None:
    await mongodb.database.users.create_index(
        "email",
        unique=True,
    )

    await mongodb.database.connections.create_index(
        [
            ("owner_id", 1),
            ("connection_name", 1),
        ],
        unique=True,
    )

    await mongodb.database.pipelines.create_index(
        [
            ("owner_id", 1),
            ("pipeline_name", 1),
        ],
        unique=True,
    )




async def close_mongodb_connection() -> None:
    if mongodb.client is not None:
        mongodb.client.close()

        mongodb.client = None
        mongodb.database = None

        print(SuccessMessages.DATABASE_DISCONNECTED)


def get_database():
    if mongodb.database is None:
        raise DatabaseException(
            ErrorMessages.DATABASE_CONNECTION_FAILED
        )

    return mongodb.database


async def execute_transaction(
    operation: Callable[[Any], Awaitable[Any]],
) -> Any:
    if mongodb.client is None:
        raise DatabaseException(
            ErrorMessages.DATABASE_CONNECTION_FAILED
        )

    try:
        async with await mongodb.client.start_session() as session:
            async with session.start_transaction():
                return await operation(session)

    except Exception as exc:
        raise DatabaseException(
            ErrorMessages.TRANSACTION_FAILED,
            error_code="TRANSACTION_FAILED",
        ) from exc
