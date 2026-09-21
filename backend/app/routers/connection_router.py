from fastapi import APIRouter, Depends, Response

from app.schema.request_schema.connection_action_request import (
    ConnectionActionRequest,
)
from app.schema.request_schema.connection_request import (
    CreateConnectionRequest,
    UpdateConnectionRequest,
)
from app.schema.response_schema.connection_action_response import (
    ConnectionActionResponse,
)
from app.schema.response_schema.connection_response import (
    ConnectionResponse,
)
from app.services.connection_service import (
    ConnectionService,
)
from app.utils.security import get_token_payload


router = APIRouter(
    prefix="/api/connections",
    tags=["Connections"],
)


@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=201,
)
async def create_connection(
    request: CreateConnectionRequest,
    user: dict = Depends(get_token_payload),
):
    return await ConnectionService.create_connection(
        owner_id=user["sub"],
        request=request,
    )


@router.get(
    "",
    response_model=list[ConnectionResponse],
)
async def get_connections(
    user: dict = Depends(get_token_payload),
):
    return await ConnectionService.get_connections(
        user_id=user["sub"],
        role=user["role"],
    )


@router.get(
    "/{connection_id}",
    response_model=ConnectionResponse,
)
async def get_connection(
    connection_id: str,
    user: dict = Depends(get_token_payload),
):
    return await ConnectionService.get_connection(
        connection_id=connection_id,
        user_id=user["sub"],
        role=user["role"],
    )


@router.patch(
    "/{connection_id}",
    response_model=ConnectionResponse,
)
async def update_connection(
    connection_id: str,
    request: UpdateConnectionRequest,
    user: dict = Depends(get_token_payload),
):
    return await ConnectionService.update_connection(
        connection_id=connection_id,
        user_id=user["sub"],
        role=user["role"],
        request=request,
    )


@router.delete(
    "/{connection_id}",
    status_code=204,
)
async def delete_connection(
    connection_id: str,
    user: dict = Depends(get_token_payload),
):
    await ConnectionService.delete_connection(
        connection_id=connection_id,
        user_id=user["sub"],
        role=user["role"],
    )

    return Response(status_code=204)


@router.post(
    "/{connection_id}/actions",
    response_model=ConnectionActionResponse,
)
async def perform_connection_action(
    connection_id: str,
    request: ConnectionActionRequest,
    user: dict = Depends(get_token_payload),
):
    return await ConnectionService.perform_action(
        connection_id=connection_id,
        user_id=user["sub"],
        role=user["role"],
        request=request,
    )
