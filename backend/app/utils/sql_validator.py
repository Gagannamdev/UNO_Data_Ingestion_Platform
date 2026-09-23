import re

from app.constants.messages import ErrorMessages
from app.exceptions.custom_exceptions import AppException


class SQLValidator:

    BLOCKED_KEYWORDS = {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE",
        "MERGE",
    }

    @staticmethod
    def validate(query: str) -> None:
        cleaned_query = query.strip()

        if not cleaned_query:
            raise AppException(
                message=ErrorMessages.SQL_QUERY_REQUIRED,
                status_code=422,
                error_code="SQL_QUERY_REQUIRED",
            )

        upper_query = cleaned_query.upper()

        if not (
            upper_query.startswith("SELECT")
            or upper_query.startswith("WITH")
        ):
            raise AppException(
                message=ErrorMessages.INVALID_SQL_QUERY,
                status_code=422,
                error_code="INVALID_SQL_QUERY",
            )

        words = set(
            re.findall(
                r"\b[A-Z]+\b",
                upper_query,
            )
        )

        blocked = words.intersection(
            SQLValidator.BLOCKED_KEYWORDS
        )

        if blocked:
            raise AppException(
                message=ErrorMessages.UNSAFE_SQL_QUERY,
                status_code=422,
                error_code="UNSAFE_SQL_QUERY",
            )

        # Allow only one SQL statement.
        query_without_last_semicolon = (
            cleaned_query.rstrip(";").strip()
        )

        if ";" in query_without_last_semicolon:
            raise AppException(
                message=ErrorMessages.MULTIPLE_SQL_STATEMENTS,
                status_code=422,
                error_code="MULTIPLE_SQL_STATEMENTS",
            )
