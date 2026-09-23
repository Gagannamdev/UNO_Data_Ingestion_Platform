from pydantic import BaseModel, Field


class PipelinePreviewRequest(BaseModel):
    limit: int = Field(
        default=20,
        ge=1,
        le=50,
    )
