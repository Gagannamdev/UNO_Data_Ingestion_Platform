from app.adapters.cockroach_adapter import (
    CockroachAdapter,
)
from app.adapters.couchbase_adapter import (
    CouchbaseAdapter,
)
from app.constants.messages import ErrorMessages
from app.enums.connection_enum import ConnectionType
from app.exceptions.custom_exceptions import AppException


def get_adapter(
    connection_type: str,
    config: dict,
):
    if (
        connection_type
        == ConnectionType.COCKROACHDB.value
    ):
        return CockroachAdapter(config)

    if (
        connection_type
        == ConnectionType.COUCHBASEDB.value
    ):
        return CouchbaseAdapter(config)

    raise AppException(
        message=ErrorMessages.INVALID_CONNECTION_CONFIG,
        status_code=422,
        error_code="INVALID_CONNECTION_TYPE",
    )
