from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    DATA_ENGINEER = "data_engineer"
