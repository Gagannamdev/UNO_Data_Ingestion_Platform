import asyncio

from app.enums.role_enum import UserRole
from app.repositories.user_repository import UserRepository
from app.schema.models.user_model import create_user_document
from app.utils.security import hash_password
from database import close_mongodb_connection, connect_to_mongodb


async def create_admin():
    await connect_to_mongodb()

    email = "admin@uno.com"
    password = "Admin@123"

    existing_admin = await UserRepository.find_by_email(email)

    if existing_admin:
        print("Admin already exists.")
        await close_mongodb_connection()
        return

    admin = create_user_document(
        name="UNO Admin",
        email=email,
        password_hash=hash_password(password),
        role=UserRole.ADMIN,
    )

    await UserRepository.create(admin)

    print("Admin created successfully.")
    print(f"Email: {email}")
    print(f"Password: {password}")

    await close_mongodb_connection()


if __name__ == "__main__":
    asyncio.run(create_admin())
