from fastapi import APIRouter, Depends, Response

from app.schema.request_schema.pipeline_preview_request import (
    PipelinePreviewRequest,
)
from app.schema.request_schema.pipeline_request import (
    CreatePipelineRequest,
    UpdatePipelineRequest,
)
from app.schema.response_schema.pipeline_preview_response import (
    PipelinePreviewResponse,
)
from app.schema.response_schema.pipeline_response import (
    PipelineResponse,
)
from app.services.pipeline_service import (
    PipelineService,
)
from app.utils.security import get_token_payload


router = APIRouter(
    prefix="/api/pipelines",
    tags=["Pipelines"],
)


@router.post(
    "",
    response_model=PipelineResponse,
    status_code=201,
)
async def create_pipeline(
    request: CreatePipelineRequest,
    user: dict = Depends(get_token_payload),
):

    return await PipelineService.create_pipeline(
        owner_id=user["sub"],
        role=user["role"],
        request=request,
    )


@router.get(
    "",
    response_model=list[PipelineResponse],
)
async def get_pipelines(
    user: dict = Depends(get_token_payload),
):

    return await PipelineService.get_pipelines(
        user_id=user["sub"],
        role=user["role"],
    )


@router.get(
    "/{pipeline_id}",
    response_model=PipelineResponse,
)
async def get_pipeline(
    pipeline_id: str,
    user: dict = Depends(get_token_payload),
):

    return await PipelineService.get_pipeline(
        pipeline_id=pipeline_id,
        user_id=user["sub"],
        role=user["role"],
    )


@router.patch(
    "/{pipeline_id}",
    response_model=PipelineResponse,
)
async def update_pipeline(
    pipeline_id: str,
    request: UpdatePipelineRequest,
    user: dict = Depends(get_token_payload),
):

    return await PipelineService.update_pipeline(
        pipeline_id=pipeline_id,
        user_id=user["sub"],
        role=user["role"],
        request=request,
    )


@router.delete(
    "/{pipeline_id}",
    status_code=204,
)
async def delete_pipeline(
    pipeline_id: str,
    user: dict = Depends(get_token_payload),
):

    await PipelineService.delete_pipeline(
        pipeline_id=pipeline_id,
        user_id=user["sub"],
        role=user["role"],
    )

    return Response(status_code=204)


@router.post(
    "/{pipeline_id}/preview",
    response_model=PipelinePreviewResponse,
)
async def preview_pipeline(
    pipeline_id: str,
    request: PipelinePreviewRequest,
    user: dict = Depends(get_token_payload),
):

    return await PipelineService.preview_pipeline(
        pipeline_id=pipeline_id,
        user_id=user["sub"],
        role=user["role"],
        limit=request.limit,
    )
