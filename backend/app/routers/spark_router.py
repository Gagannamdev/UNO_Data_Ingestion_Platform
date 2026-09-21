from fastapi import APIRouter

from app.services.spark.spark_service import (
    SparkService,
)


router = APIRouter(
    prefix="/api/spark",
    tags=["Spark"],
)


@router.get("/health")
async def spark_health():
    spark = SparkService.get_spark()

    return {
        "success": True,
        "message": "Spark engine is running",
        "application": spark.sparkContext.appName,
        "master": spark.sparkContext.master,
    }
