import asyncio
from datetime import timedelta
from typing import Any

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
            host = f"couchbases://{host}"

        authenticator = PasswordAuthenticator(
            self.config["username"],
            self.config["password"],
        )

        options = ClusterOptions(
            authenticator
        )

        if host.startswith("couchbases://"):
            options.apply_profile(
                "wan_development"
            )

        cluster = Cluster.connect(
            host,
            options,
        )

        cluster.wait_until_ready(
            timedelta(seconds=15)
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
            return await asyncio.to_thread(
                connect
            )

        except Exception as exc:
            return {
                "success": False,
                "message": (
                    ErrorMessages
                    .CONNECTION_TEST_FAILED
                ),
                "detail": str(exc),
            }

    async def list_tables(self) -> list[str]:

        def fetch_collections():
            cluster = self._connect()

            try:
                bucket_name = self.config["bucket"]

                selected_scope = self.config.get(
                    "scope"
                )

                bucket = cluster.bucket(
                    bucket_name
                )

                scopes = (
                    bucket.collections()
                    .get_all_scopes()
                )

                collections = []

                for scope in scopes:

                    if (
                        selected_scope
                        and scope.name
                        != selected_scope
                    ):
                        continue

                    for collection in (
                        scope.collections
                    ):
                        collections.append(
                            f"{scope.name}."
                            f"{collection.name}"
                        )

                return collections

            finally:
                cluster.close()

        try:
            return await asyncio.to_thread(
                fetch_collections
            )

        except Exception as exc:
            raise RuntimeError(
                ErrorMessages
                .CONNECTION_OBJECT_FETCH_FAILED
            ) from exc

    async def preview_data(
        self,
        collection_name: str,
        limit: int = 20,
    ) -> list[dict]:

        limit = min(
            max(limit, 1),
            50,
        )

        def fetch_data():
            cluster = self._connect()

            try:
                bucket = self.config["bucket"]

                scope = self.config.get(
                    "scope",
                    "_default",
                )

                query = f"""
                    SELECT
                        META(data).id AS id,
                        data.*
                    FROM
                        `{bucket}`.`{scope}`.`{collection_name}` AS data
                    LIMIT {limit}
                """

                result = cluster.query(query)

                return [
                    dict(row)
                    for row in result
                ]

            finally:
                cluster.close()

        try:
            return await asyncio.to_thread(
                fetch_data
            )

        except Exception as exc:
            raise RuntimeError(
                ErrorMessages
                .CONNECTION_PREVIEW_FAILED
            ) from exc

    async def read_data(
        self,
        collection_name: str,
    ) -> list[dict]:

        def fetch_all_data():

            cluster = self._connect()

            try:
                bucket = self.config["bucket"]

                scope = self.config.get(
                    "scope",
                    "_default",
                )

                query = f"""
                    SELECT
                        META(data).id AS id,
                        data.*
                    FROM
                        `{bucket}`.`{scope}`.`{collection_name}` AS data
                """

                result = cluster.query(query)

                return [
                    dict(row)
                    for row in result
                ]

            finally:
                cluster.close()

        try:
            return await asyncio.to_thread(
                fetch_all_data
            )

        except Exception as exc:
            raise RuntimeError(
                "Couchbase data read failed"
            ) from exc

    async def write_data(
        self,
        rows: list[dict[str, Any]],
        collection_name: str,
        write_mode: str = "append",
    ) -> dict:

        if not rows:
            return {
                "success": True,
                "records_written": 0,
            }

        def write_rows():

            cluster = self._connect()

            try:
                bucket_name = self.config["bucket"]

                scope_name = self.config.get(
                    "scope",
                    "_default",
                )

                bucket = cluster.bucket(
                    bucket_name
                )

                collection = (
                    bucket.scope(scope_name)
                    .collection(collection_name)
                )

                # Overwrite mode removes
                # existing documents first.
                if write_mode == "overwrite":

                    query = f"""
                        DELETE FROM
                        `{bucket_name}`.`{scope_name}`.`{collection_name}`
                    """

                    cluster.query(query).execute()

                written = 0

                for index, row in enumerate(rows):

                    document = dict(row)

                    # Use source document ID
                    # when available.
                    document_id = document.pop(
                        "id",
                        None,
                    )

                    # Use document_id if available.
                    if not document_id:
                        document_id = document.pop(
                            "document_id",
                            None,
                        )

                    # Fallback ID.
                    if not document_id:
                        document_id = (
                            f"pipeline_document_{index}"
                        )

                    collection.upsert(
                        str(document_id),
                        document,
                    )

                    written += 1

                return {
                    "success": True,
                    "records_written": written,
                }

            finally:
                cluster.close()

        try:
            return await asyncio.to_thread(
                write_rows
            )

        except Exception as exc:
            raise RuntimeError(
                "Couchbase data write failed"
            ) from exc

    async def close(self) -> None:
        return None
