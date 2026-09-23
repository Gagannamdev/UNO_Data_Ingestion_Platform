from fastapi import Request
from fastapi.responses import JSONResponse

from app.constants.messages import ErrorMessages
from app.exceptions.custom_exceptions import AppException


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """
    Handles known application exceptions.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )


async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handles unexpected exceptions.

    Internal implementation details are not exposed
    to the API client.
    """

    print(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": ErrorMessages.INTERNAL_SERVER_ERROR,
        },
    )
