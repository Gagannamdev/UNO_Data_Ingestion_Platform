from datetime import datetime, timezone

from app.enums.connection_enum import ConnectionStatus


def create_connection_document(
    owner_id: str,
    data: dict,
    encrypted_password: str,
) -> dict:

    return {
        "owner_id": owner_id,
        "connection_name": data["connection_name"],
        "connection_type": data["connection_type"],
        "host": data["host"],
        "port": data.get("port"),
        "database_name": data.get("database_name"),
        "username": data["username"],
        "encrypted_password": encrypted_password,
        "ssl_mode": data.get("ssl_mode"),
        "bucket": data.get("bucket"),
        "scope": data.get("scope"),
        "collection": data.get("collection"),
        "status": ConnectionStatus.NOT_TESTED.value,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
