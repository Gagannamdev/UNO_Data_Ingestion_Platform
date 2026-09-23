from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from app.enums.connection_enum import ConnectionType


class CreateConnectionRequest(BaseModel):
    connection_name: str = Field(
        min_length=2,
        max_length=100,
    )

    connection_type: ConnectionType

    host: str = Field(
        min_length=2,
        max_length=255,
    )

    port: Optional[int] = None

    database_name: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    username: str = Field(
        min_length=1,
        max_length=100,
    )

    password: str = Field(
        min_length=1,
        max_length=255,
    )

    ssl_mode: Optional[str] = None

    bucket: Optional[str] = None
    scope: Optional[str] = None
    collection: Optional[str] = None

    @field_validator("connection_name", "host", "username")
    @classmethod
    def strip_required_values(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value

    @field_validator("port")
    @classmethod
    def validate_port(cls, value):
        if value is not None and not 1 <= value <= 65535:
            raise ValueError(
                "Port must be between 1 and 65535"
            )

        return value

    @model_validator(mode="after")
    def validate_connection_fields(self):
        if self.connection_type == ConnectionType.COCKROACHDB:
            required = [
                self.port,
                self.database_name,
            ]

            if not all(required):
                raise ValueError(
                    "CockroachDB requires port and database_name"
                )

        if self.connection_type == ConnectionType.COUCHBASEDB:
            if not self.bucket:
                raise ValueError(
                    "CouchbaseDB requires bucket"
                )

        return self


class UpdateConnectionRequest(BaseModel):
    connection_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    host: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    ssl_mode: Optional[str] = None

    bucket: Optional[str] = None
    scope: Optional[str] = None
    collection: Optional[str] = None

    @field_validator("port")
    @classmethod
    def validate_port(cls, value):
        if value is not None and not 1 <= value <= 65535:
            raise ValueError(
                "Port must be between 1 and 65535"
            )

        return value
