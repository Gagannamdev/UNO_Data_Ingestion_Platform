from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.enums.connection_enum import ConnectionAction


class ConnectionActionRequest(BaseModel):
    action: ConnectionAction

    object_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=50,
    )

    @model_validator(mode="after")
    def validate_action_fields(self):
        if (
            self.action == ConnectionAction.PREVIEW
            and not self.object_name
        ):
            raise ValueError(
                "object_name is required for preview action"
            )

        return self
