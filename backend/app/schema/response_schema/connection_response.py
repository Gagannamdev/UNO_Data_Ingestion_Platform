from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ConnectionResponse(BaseModel):
    id: str
    connection_name: str
    connection_type: str
    host: str
    port: Optional[int]
    database_name: Optional[str]
    username: str

    ssl_mode: Optional[str]

    bucket: Optional[str]
    scope: Optional[str]
    collection: Optional[str]

    status: str

    created_at: datetime
    updated_at: datetime
