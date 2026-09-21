import asyncio

import psycopg2

from app.constants.messages import ErrorMessages


class CockroachAdapter:

    def __init__(self, config: dict):
        self.config = config

    def _connect(self):
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database_name"],
            user=self.config["username"],
            password=self.config["password"],
            sslmode=self.config.get(
                "ssl_mode",
                "require",
            ),
            connect_timeout=5,
        )

    async def test_connection(self) -> dict:
        def connect():
            connection = self._connect()

            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                return {
                    "success": True,
                    "message": (
                        "CockroachDB connection successful"
                    ),
                }

            finally:
                connection.close()

        try:
            return await asyncio.to_thread(connect)

        except Exception as exc:
            return {
                "success": False,
                "message": (
                    ErrorMessages.CONNECTION_TEST_FAILED
                ),
                "detail": str(exc),
            }

    async def list_tables(self) -> list[str]:
        def fetch_tables():
            connection = self._connect()

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                        """
                    )

                    return [
                        row[0]
                        for row in cursor.fetchall()
                    ]

            finally:
                connection.close()

        return await asyncio.to_thread(
            fetch_tables
        )

    async def preview_data(
        self,
        table_name: str,
        limit: int = 20,
    ) -> list[dict]:

        if not table_name.replace("_", "").isalnum():
            raise ValueError(
                "Invalid table name"
            )

        limit = min(max(limit, 1), 50)

        def fetch_data():
            connection = self._connect()

            try:
                with connection.cursor() as cursor:
                    query = (
                        f'SELECT * FROM "{table_name}" '
                        f"LIMIT {limit}"
                    )

                    cursor.execute(query)

                    columns = [
                        description[0]
                        for description in cursor.description
                    ]

                    return [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]

            finally:
                connection.close()

        return await asyncio.to_thread(
            fetch_data
        )

    async def close(self) -> None:
        return None
