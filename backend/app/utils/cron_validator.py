from croniter import croniter

from app.constants.messages import ErrorMessages
from app.exceptions.custom_exceptions import AppException


class CronValidator:

    @staticmethod
    def validate(cron_expression: str) -> None:
        if not cron_expression:
            raise AppException(
                message=ErrorMessages.CRON_REQUIRED,
                status_code=422,
                error_code="CRON_REQUIRED",
            )

        if not croniter.is_valid(cron_expression):
            raise AppException(
                message=ErrorMessages.INVALID_CRON,
                status_code=422,
                error_code="INVALID_CRON",
            )
