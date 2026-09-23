from typing import Any, Optional

from pydantic import BaseModel


class ConnectionActionResponse(BaseModel):
    success: bool
    message: str

    status: Optional[str] = None

    data: Optional[Any] = None
