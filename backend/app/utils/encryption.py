from cryptography.fernet import Fernet

from configs.config import settings


fernet = Fernet(
    settings.encryption_key.encode()
)


def encrypt_value(value: str) -> str:
    return fernet.encrypt(
        value.encode("utf-8")
    ).decode("utf-8")


def decrypt_value(value: str) -> str:
    return fernet.decrypt(
        value.encode("utf-8")
    ).decode("utf-8")
