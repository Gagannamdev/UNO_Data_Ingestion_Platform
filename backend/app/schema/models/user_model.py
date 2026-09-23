from datetime import datetime, timezone

from app.enums.role_enum import UserRole


def create_user_document(
    name: str,
    email: str,
    password_hash: str,
    role: UserRole,
) -> dict:
    return {
        "name": name,
        "email": email.lower(),
        "password_hash": password_hash,
        "role": role.value,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
