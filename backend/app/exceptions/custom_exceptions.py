from typing import Optional


class AppException(Exception):
    """
    Base exception for application-specific errors.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

        super().__init__(message)


class DatabaseException(AppException):
    """
    Raised when a database operation fails.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "DATABASE_ERROR",
    ):
        super().__init__(
            message=message,
            status_code=503,
            error_code=error_code,
        )


class NotFoundException(AppException):
    """
    Raised when requested resource does not exist.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "NOT_FOUND",
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code=error_code,
        )


class ConflictException(AppException):
    """
    Raised when resource conflicts with existing data.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "CONFLICT",
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code=error_code,
        )


class ForbiddenException(AppException):
    """
    Raised when authenticated user does not have permission.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "FORBIDDEN",
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code=error_code,
        )


class UnauthorizedException(AppException):
    """
    Raised when authentication fails.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "UNAUTHORIZED",
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code,
        )
