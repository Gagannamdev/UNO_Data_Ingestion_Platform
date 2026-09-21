from datetime import datetime, timezone

from app.adapters.adapter_factory import get_adapter
from app.constants.messages import (
    ErrorMessages,
    SuccessMessages,
)
from app.enums.connection_enum import (
    ConnectionAction,
    ConnectionStatus,
)
from app.exceptions.custom_exceptions import (
    AppException,
    NotFoundException,
)
from app.repositories.connection_repository import (
    ConnectionRepository,
)
from app.schema.models.connection_model import (
    create_connection_document,
)
from app.schema.request_schema.connection_request import (
    CreateConnectionRequest,
)
from app.utils.encryption import (
    decrypt_value,
    encrypt_value,
)


class ConnectionService:

    @staticmethod
    def format_connection(
        connection: dict,
    ) -> dict:
        return {
            "id": str(connection["_id"]),
            "connection_name": connection[
                "connection_name"
            ],
            "connection_type": connection[
                "connection_type"
            ],
            "host": connection["host"],
            "port": connection.get("port"),
            "database_name": connection.get(
                "database_name"
            ),
            "username": connection["username"],
            "ssl_mode": connection.get("ssl_mode"),
            "bucket": connection.get("bucket"),
            "scope": connection.get("scope"),
            "collection": connection.get("collection"),
            "status": connection["status"],
            "created_at": connection["created_at"],
            "updated_at": connection["updated_at"],
        }

    @staticmethod
    def build_adapter_config(
        connection: dict,
    ) -> dict:
        return {
            "host": connection["host"],
            "port": connection.get("port"),
            "database_name": connection.get(
                "database_name"
            ),
            "username": connection["username"],
            "password": decrypt_value(
                connection["encrypted_password"]
            ),
            "ssl_mode": connection.get("ssl_mode"),
            "bucket": connection.get("bucket"),
            "scope": connection.get("scope"),
            "collection": connection.get("collection"),
        }

    @staticmethod
    async def create_connection(
        owner_id: str,
        request: CreateConnectionRequest,
    ) -> dict:

        data = request.model_dump()

        data["connection_type"] = (
            request.connection_type.value
        )

        connection = create_connection_document(
            owner_id=owner_id,
            data=data,
            encrypted_password=encrypt_value(
                request.password
            ),
        )

        created = await ConnectionRepository.create(
            connection
        )

        return ConnectionService.format_connection(
            created
        )

    @staticmethod
    async def get_connections(
        user_id: str,
        role: str,
    ) -> list[dict]:

        owner_id = (
            None
            if role == "admin"
            else user_id
        )

        connections = (
            await ConnectionRepository.find_all(
                owner_id=owner_id
            )
        )

        return [
            ConnectionService.format_connection(
                connection
            )
            for connection in connections
        ]

    @staticmethod
    async def get_connection(
        connection_id: str,
        user_id: str,
        role: str,
    ) -> dict:

        connection = (
            await ConnectionRepository.find_by_id(
                connection_id
            )
        )

        ConnectionService.validate_access(
            connection,
            user_id,
            role,
        )

        return ConnectionService.format_connection(
            connection
        )

    @staticmethod
    async def update_connection(
        connection_id: str,
        user_id: str,
        role: str,
        request,
    ) -> dict:

        connection = (
            await ConnectionRepository.find_by_id(
                connection_id
            )
        )

        ConnectionService.validate_access(
            connection,
            user_id,
            role,
        )

        updates = request.model_dump(
            exclude_unset=True
        )

        new_password = updates.pop(
            "password",
            None,
        )

        current_data = {
            "connection_name": connection[
                "connection_name"
            ],
            "connection_type": connection[
                "connection_type"
            ],
            "host": connection["host"],
            "port": connection.get("port"),
            "database_name": connection.get(
                "database_name"
            ),
            "username": connection["username"],
            "password": decrypt_value(
                connection[
                    "encrypted_password"
                ]
            ),
            "ssl_mode": connection.get(
                "ssl_mode"
            ),
            "bucket": connection.get("bucket"),
            "scope": connection.get("scope"),
            "collection": connection.get(
                "collection"
            ),
        }

        current_data.update(updates)

        validated = CreateConnectionRequest(
            **current_data
        )

        final_updates = validated.model_dump()

        final_updates.pop("password")

        final_updates["connection_type"] = (
            validated.connection_type.value
        )

        if new_password:
            final_updates[
                "encrypted_password"
            ] = encrypt_value(
                new_password
            )

        final_updates["status"] = (
            ConnectionStatus.NOT_TESTED.value
        )

        final_updates["updated_at"] = (
            datetime.now(timezone.utc)
        )

        updated = await ConnectionRepository.update(
            connection_id,
            final_updates,
        )

        return ConnectionService.format_connection(
            updated
        )

    @staticmethod
    async def delete_connection(
        connection_id: str,
        user_id: str,
        role: str,
    ) -> None:

        connection = (
            await ConnectionRepository.find_by_id(
                connection_id
            )
        )

        ConnectionService.validate_access(
            connection,
            user_id,
            role,
        )

        await ConnectionRepository.delete(
            connection_id
        )

    @staticmethod
    async def perform_action(
        connection_id: str,
        user_id: str,
        role: str,
        request,
    ) -> dict:

        connection = (
            await ConnectionRepository.find_by_id(
                connection_id
            )
        )

        ConnectionService.validate_access(
            connection,
            user_id,
            role,
        )

        config = ConnectionService.build_adapter_config(
            connection
        )

        adapter = get_adapter(
            connection["connection_type"],
            config,
        )

        if request.action == ConnectionAction.TEST:
            return await ConnectionService.test_connection(
                connection_id,
                adapter,
            )

        if request.action == ConnectionAction.TABLES:
            return await ConnectionService.get_objects(
                connection_id,
                adapter,
            )

        if request.action == ConnectionAction.PREVIEW:
            return await ConnectionService.preview_data(
                connection_id=connection_id,
                adapter=adapter,
                object_name=request.object_name,
                limit=request.limit,
            )

        raise AppException(
            message=ErrorMessages.INVALID_CONNECTION_ACTION,
            status_code=422,
            error_code="INVALID_CONNECTION_ACTION",
        )

    @staticmethod
    async def test_connection(
        connection_id: str,
        adapter,
    ) -> dict:

        result = await adapter.test_connection()

        if result["success"]:
            status = ConnectionStatus.CONNECTED.value

            await ConnectionRepository.update_status(
                connection_id,
                status,
            )

            return {
                "success": True,
                "message": (
                    SuccessMessages.CONNECTION_TEST_SUCCESS
                ),
                "status": status,
                "data": None,
            }

        status = ConnectionStatus.FAILED.value

        await ConnectionRepository.update_status(
            connection_id,
            status,
        )

        return {
            "success": False,
            "message": result["message"],
            "status": status,
            "data": None,
        }

    @staticmethod
    async def get_objects(
        connection_id: str,
        adapter,
    ) -> dict:

        try:
            objects = await adapter.list_tables()

            await ConnectionRepository.update_status(
                connection_id,
                ConnectionStatus.CONNECTED.value,
            )

            return {
                "success": True,
                "message": (
                    SuccessMessages
                    .CONNECTION_OBJECTS_FETCHED
                ),
                "status": (
                    ConnectionStatus.CONNECTED.value
                ),
                "data": objects,
            }

        except Exception as exc:
            await ConnectionRepository.update_status(
                connection_id,
                ConnectionStatus.FAILED.value,
            )

            raise AppException(
                message=(
                    ErrorMessages
                    .CONNECTION_OBJECT_FETCH_FAILED
                ),
                status_code=400,
                error_code=(
                    "CONNECTION_OBJECT_FETCH_FAILED"
                ),
            ) from exc

    @staticmethod
    async def preview_data(
        connection_id: str,
        adapter,
        object_name: str,
        limit: int,
    ) -> dict:

        try:
            rows = await adapter.preview_data(
                object_name,
                limit,
            )

            await ConnectionRepository.update_status(
                connection_id,
                ConnectionStatus.CONNECTED.value,
            )

            return {
                "success": True,
                "message": (
                    SuccessMessages
                    .CONNECTION_PREVIEW_FETCHED
                ),
                "status": (
                    ConnectionStatus.CONNECTED.value
                ),
                "data": rows,
            }

        except Exception as exc:
            await ConnectionRepository.update_status(
                connection_id,
                ConnectionStatus.FAILED.value,
            )

            raise AppException(
                message=(
                    ErrorMessages
                    .CONNECTION_PREVIEW_FAILED
                ),
                status_code=400,
                error_code="CONNECTION_PREVIEW_FAILED",
            ) from exc

    @staticmethod
    def validate_access(
        connection,
        user_id: str,
        role: str,
    ) -> None:

        if not connection:
            raise NotFoundException(
                ErrorMessages.CONNECTION_NOT_FOUND,
                error_code="CONNECTION_NOT_FOUND",
            )

        if (
            role != "admin"
            and connection["owner_id"] != user_id
        ):
            raise NotFoundException(
                ErrorMessages.CONNECTION_NOT_FOUND,
                error_code="CONNECTION_NOT_FOUND",
            )
