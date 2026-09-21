from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.constants.messages import SuccessMessages
from app.exceptions.custom_exceptions import AppException
from app.handler.exception_handler import (
    app_exception_handler,
    global_exception_handler,
)
from app.routers.auth_router import router as auth_router
from app.routers.connection_router import (
    router as connection_router,
)
from app.routers.user_router import router as user_router
from configs.config import settings
from database import (
    close_mongodb_connection,
    connect_to_mongodb,
)
from app.routers.pipeline_router import (
    router as pipeline_router,
)
from app.routers.spark_router import (
    router as spark_router,
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    yield
    await close_mongodb_connection()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "UNO Data Ingestion & Transformation Platform API"
    ),
    lifespan=lifespan,
)


app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    Exception,
    global_exception_handler,
)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(connection_router)
app.include_router(pipeline_router)
app.include_router(spark_router)



@app.get("/")
async def root():
    return {
        "success": True,
        "message": SuccessMessages.API_RUNNING,
    }


@app.get("/health")
async def health_check():
    return {
        "success": True,
        "status": "healthy",
        "application": settings.app_name,
        "database": "connected",
    }
