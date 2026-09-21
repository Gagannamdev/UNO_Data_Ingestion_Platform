import asyncio

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions

from app.constants.messages import ErrorMessages


class CouchbaseAdapter:

    def __init__(self, config: dict):
        self.config = config

    def _connect(self):
        host = self.config["host"]

        if "://" not in host:
            host = f"couchbase://{host}"

        authenticator = PasswordAuthenticator(
            self.config["username"],
            self.config["password"],
        )

        cluster = Cluster(
            host,
            ClusterOptions(authenticator),
        )

        cluster.wait_until_ready(
            timeout=5,
        )

        return cluster

    async def test_connection(self) -> dict:

        def connect():
            cluster = self._connect()

            try:
                cluster.ping()

                return {
                    "success": True,
                    "message": (
                        "CouchbaseDB connection successful"
                    ),
                }

            finally:
                cluster.close()

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

        def fetch_collections():
            cluster = self._connect()

            try:
                bucket_name = self.config["bucket"]

                bucket = cluster.bucket(
                    bucket_name
                )

                bucket.wait_until_ready(
                    timeout=5
                )

                scopes = bucket.collections().get_all_scopes()

                collections = []

                for scope in scopes:
                    for collection in scope.collections:
                        collections.append(
                            f"{scope.name}.{collection.name}"
                        )

                return collections

            finally:
                cluster.close()

        return await asyncio.to_thread(
            fetch_collections
        )

    async def preview_data(
        self,
        collection_name: str,
        limit: int = 20,
    ) -> list[dict]:

        limit = min(max(limit, 1), 50)

        def fetch_data():
            cluster = self._connect()

            try:
                bucket = self.config["bucket"]

                scope = self.config.get(
                    "scope",
                    "_default",
                )

                query = f"""
                    SELECT META().id, data.*
                    FROM `{bucket}`.`{scope}`.`{collection_name}` AS data
                    LIMIT {limit}
                """

                result = cluster.query(query)

                return [
                    dict(row)
                    for row in result
                ]

            finally:
                cluster.close()

        return await asyncio.to_thread(
            fetch_data
        )

    async def close(self) -> None:
        return None
