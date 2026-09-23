from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class TransformationStepResponse(BaseModel):
    step_name: str
    query: str


class PipelineResponse(BaseModel):
    id: str
    owner_id: str

    pipeline_name: str
    description: Optional[str]

    source: dict[str, Any]

    transformation: dict[str, Any]

    destination: dict[str, Any]

    schedule: dict[str, Any]

    status: str
    last_run_status: Optional[str]
    last_run_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime
