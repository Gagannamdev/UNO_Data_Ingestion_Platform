import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.constants.messages import ErrorMessages


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not re.fullmatch(r"[A-Za-z ]+", value):
            raise ValueError(ErrorMessages.INVALID_NAME)

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        has_upper = re.search(r"[A-Z]", value)
        has_lower = re.search(r"[a-z]", value)
        has_number = re.search(r"\d", value)
        has_special = re.search(r"[^A-Za-z0-9]", value)

        if not all([
            has_upper,
            has_lower,
            has_number,
            has_special,
        ]):
            raise ValueError(ErrorMessages.WEAK_PASSWORD)

        return value
