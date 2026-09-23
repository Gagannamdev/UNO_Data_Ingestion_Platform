import os
from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

from app.constants.messages import ErrorMessages
from app.exceptions.custom_exceptions import AppException


class SparkService:

    _spark: SparkSession | None = None

    @classmethod
    def get_spark(cls) -> SparkSession:
        if cls._spark is None:
            try:
                python_executable = os.path.abspath(
                    os.sys.executable
                )

                os.environ["PYSPARK_PYTHON"] = (
                    python_executable
                )

                os.environ["PYSPARK_DRIVER_PYTHON"] = (
                    python_executable
                )

                cls._spark = (
                    SparkSession.builder
                    .appName(
                        "UNO-Data-Ingestion-Platform"
                    )
                    .master("local[*]")
                    .config(
                        "spark.sql.shuffle.partitions",
                        "4",
                    )
                    .config(
                        "spark.pyspark.python",
                        python_executable,
                    )
                    .config(
                        "spark.pyspark.driver.python",
                        python_executable,
                    )
                    .getOrCreate()
                )

                cls._spark.sparkContext.setLogLevel(
                    "WARN"
                )

            except Exception as exc:
                raise AppException(
                    message=ErrorMessages.SPARK_START_FAILED,
                    status_code=503,
                    error_code="SPARK_START_FAILED",
                ) from exc

        return cls._spark

    @classmethod
    def stop_spark(cls) -> None:
        if cls._spark is not None:
            cls._spark.stop()
            cls._spark = None

    @classmethod
    def create_dataframe(
        cls,
        rows: list[dict[str, Any]],
    ) -> DataFrame:

        try:
            spark = cls.get_spark()

            if not rows:
                raise AppException(
                    message=ErrorMessages.NO_SOURCE_DATA,
                    status_code=422,
                    error_code="NO_SOURCE_DATA",
                )

            return spark.createDataFrame(rows)

        except AppException:
            raise

        except Exception as exc:
            raise AppException(
                message=ErrorMessages.SPARK_DATAFRAME_FAILED,
                status_code=400,
                error_code="SPARK_DATAFRAME_FAILED",
            ) from exc

    @classmethod
    def preview_transformation(
        cls,
        rows,
        queries,
        limit=20,
    ):
        if not queries:
            return rows[:limit]

        dataframe = cls.create_dataframe(rows)

        try:
            spark = cls.get_spark()

            dataframe.createOrReplaceTempView(
                "source_data"
            )

            for index, query in enumerate(
                queries,
                start=1,
            ):

                result = spark.sql(query)

                view_name = f"step_{index}"

                result.createOrReplaceTempView(
                    view_name
                )

                dataframe = result

            return [
                row.asDict()
                for row in dataframe
                .limit(limit)
                .collect()
            ]

        except Exception as exc:
            raise AppException(
                message=ErrorMessages.TRANSFORMATION_FAILED,
                status_code=422,
                error_code="TRANSFORMATION_FAILED",
            ) from exc

    @classmethod
    def preview_steps(
        cls,
        rows,
        steps,
        limit=20,
    ):

        if not steps:
            return []

        dataframe = cls.create_dataframe(rows)

        try:
            spark = cls.get_spark()

            dataframe.createOrReplaceTempView(
                "source_data"
            )

            previews = []

            for index, step in enumerate(
                steps,
                start=1,
            ):

                query = (
                    step["query"]
                    if isinstance(step, dict)
                    else step.query
                )

                result = spark.sql(query)

                view_name = f"step_{index}"

                result.createOrReplaceTempView(
                    view_name
                )

                preview_data = [
                    row.asDict()
                    for row in result
                    .limit(limit)
                    .collect()
                ]

                previews.append(
                    {
                        "step_name": (
                            step["step_name"]
                            if isinstance(step, dict)
                            else step.step_name
                        ),
                        "data": preview_data,
                    }
                )

                dataframe = result

            return previews

        except Exception as exc:
            raise AppException(
                message=ErrorMessages.TRANSFORMATION_FAILED,
                status_code=422,
                error_code="TRANSFORMATION_FAILED",
            ) from exc

    @classmethod
    def execute_steps(
        cls,
        rows: list[dict[str, Any]],
        steps,
    ) -> DataFrame:

        if not rows:
            raise AppException(
                message=ErrorMessages.NO_SOURCE_DATA,
                status_code=422,
                error_code="NO_SOURCE_DATA",
            )

        dataframe = cls.create_dataframe(rows)

        try:
            spark = cls.get_spark()

            # Source data is available to the
            # first transformation as source_data.
            dataframe.createOrReplaceTempView(
                "source_data"
            )

            # If there are no transformation steps,
            # return the original source dataframe.
            if not steps:
                return dataframe

            for index, step in enumerate(
                steps,
                start=1,
            ):

                query = (
                    step["query"]
                    if isinstance(step, dict)
                    else step.query
                )

                result = spark.sql(query)

                view_name = f"step_{index}"

                result.createOrReplaceTempView(
                    view_name
                )

                dataframe = result

            # Return the complete Spark DataFrame.
            
            return dataframe

        except AppException:
            raise

        except Exception as exc:
            raise AppException(
                message=ErrorMessages.TRANSFORMATION_FAILED,
                status_code=422,
                error_code="TRANSFORMATION_FAILED",
            ) from exc
