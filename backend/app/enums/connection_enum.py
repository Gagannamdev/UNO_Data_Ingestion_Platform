from enum import Enum


class ConnectionType(str, Enum):
    COCKROACHDB = "cockroachdb"
    COUCHBASEDB = "couchbasedb"


class ConnectionStatus(str, Enum):
    NOT_TESTED = "not_tested"
    CONNECTED = "connected"
    FAILED = "failed"

class ConnectionAction(str, Enum):
    TEST = "test"
    TABLES = "tables"
    PREVIEW = "preview"
