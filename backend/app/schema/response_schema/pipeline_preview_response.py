from typing import Any

from pydantic import BaseModel


class TransformationPreview(BaseModel):
    step_name: str
    data: list[dict[str, Any]]


class PipelinePreviewResponse(BaseModel):
    success: bool
    message: str
    pipeline_id: str
    source_data: list[dict[str, Any]]
    transformation_steps: list[TransformationPreview]
    final_data: list[dict[str, Any]]
