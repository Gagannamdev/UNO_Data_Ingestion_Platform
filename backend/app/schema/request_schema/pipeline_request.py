from typing import Optional

from pydantic import BaseModel, Field

from app.enums.pipeline_enum import WriteMode


class TransformationStep(BaseModel):
    step_name: str = Field(
        min_length=1,
        max_length=100,
    )

    query: str = Field(
        min_length=1,
        max_length=10000,
    )


class CreatePipelineRequest(BaseModel):
    pipeline_name: str = Field(
        min_length=2,
        max_length=100,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    source_connection_id: str = Field(
        min_length=1,
    )

    source_object_name: str = Field(
        min_length=1,
        max_length=150,
    )

    transformation_steps: list[
        TransformationStep
    ] = Field(
        default_factory=list,
        max_length=20,
    )

    destination_connection_id: str = Field(
        min_length=1,
    )

    destination_object_name: str = Field(
        min_length=1,
        max_length=150,
    )

    write_mode: WriteMode

    schedule_enabled: bool = False

    cron: Optional[str] = Field(
        default=None,
        max_length=100,
    )


class UpdatePipelineRequest(BaseModel):
    pipeline_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    source_connection_id: Optional[str] = None

    source_object_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    transformation_steps: Optional[
        list[TransformationStep]
    ] = Field(
        default=None,
        max_length=20,
    )

    destination_connection_id: Optional[str] = None

    destination_object_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    write_mode: Optional[WriteMode] = None

    schedule_enabled: Optional[bool] = None

    cron: Optional[str] = Field(
        default=None,
        max_length=100,
    )
