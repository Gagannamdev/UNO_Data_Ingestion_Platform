from fastapi import APIRouter, Depends

from app.schema.request_schema.user_request import CreateUserRequest
from app.schema.response_schema.user_response import UserResponse
from app.services.user_service import UserService
from app.utils.security import (
    get_token_payload,
    require_admin,
)

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
)
async def create_user(
    request: CreateUserRequest,
    _: dict = Depends(require_admin),
):
    return await UserService.create_data_engineer(
        name=request.name,
        email=request.email,
        password=request.password,
    )


@router.get(
    "",
    response_model=list[UserResponse],
)
async def get_users(
    _: dict = Depends(require_admin),
):
    return await UserService.get_all_users()


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_my_profile(
    payload: dict = Depends(get_token_payload),
):
    return await UserService.get_user_by_id(
        payload["sub"]
    )
