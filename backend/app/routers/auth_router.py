from fastapi import APIRouter

from app.schema.request_schema.auth_request import LoginRequest
from app.schema.response_schema.auth_response import LoginResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(request: LoginRequest):
    return await AuthService.login(
        email=request.email,
        password=request.password,
    )
  