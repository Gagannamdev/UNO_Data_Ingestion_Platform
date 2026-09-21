from datetime import datetime, timezone

from app.constants.messages import (
    ErrorMessages,
    SuccessMessages,
)
from app.enums.connection_enum import ConnectionAction
from app.enums.pipeline_enum import PipelineStatus
from app.exceptions.custom_exceptions import (
    NotFoundException,
)
from app.repositories.connection_repository import (
    ConnectionRepository,
)
from app.repositories.pipeline_repository import (
    PipelineRepository,
)
from app.schema.models.pipeline_model import (
    create_pipeline_document,
)
from app.schema.request_schema.connection_action_request import (
    ConnectionActionRequest,
)
from app.services.connection_service import ConnectionService
from app.services.spark.spark_service import SparkService
from app.utils.cron_validator import CronValidator
from app.utils.sql_validator import SQLValidator


class PipelineService:

    @staticmethod
    def format_pipeline(pipeline: dict) -> dict:
        return {
            "id": str(pipeline["_id"]),
            "owner_id": pipeline["owner_id"],
            "pipeline_name": pipeline["pipeline_name"],
            "description": pipeline.get("description"),
            "source": pipeline.get("source", {}),
            "transformation": pipeline.get(
                "transformation",
                {},
            ),
            "destination": pipeline.get(
                "destination",
                {},
            ),
            "schedule": pipeline.get(
                "schedule",
                {},
            ),
            "status": pipeline.get(
                "status",
                PipelineStatus.INVALID.value,
            ),
            "last_run_status": pipeline.get(
                "last_run_status"
            ),
            "last_run_at": pipeline.get(
                "last_run_at"
            ),
            "created_at": pipeline["created_at"],
            "updated_at": pipeline["updated_at"],
        }

    @staticmethod
    async def validate_connection(
        connection_id: str,
        user_id: str,
        role: str,
    ) -> dict:

        connection = (
            await ConnectionRepository.find_by_id(
                connection_id
            )
        )

        if not connection:
            raise NotFoundException(
                ErrorMessages.CONNECTION_NOT_FOUND,
                error_code="CONNECTION_NOT_FOUND",
            )

        if (
            role != "admin"
            and connection["owner_id"] != user_id
        ):
            raise NotFoundException(
                ErrorMessages.CONNECTION_NOT_FOUND,
                error_code="CONNECTION_NOT_FOUND",
            )

        return connection

    @staticmethod
    def validate_transformations(
        steps: list,
    ) -> None:

        for step in steps:

            query = (
                step["query"]
                if isinstance(step, dict)
                else step.query
            )

            SQLValidator.validate(query)

    @staticmethod
    def validate_schedule(
        schedule_enabled: bool,
        cron: str | None,
    ) -> None:

        if schedule_enabled:
            CronValidator.validate(cron)

    @staticmethod
    async def create_pipeline(
        owner_id: str,
        role: str,
        request,
    ) -> dict:

        await PipelineService.validate_connection(
            request.source_connection_id,
            owner_id,
            role,
        )

        await PipelineService.validate_connection(
            request.destination_connection_id,
            owner_id,
            role,
        )

        PipelineService.validate_transformations(
            request.transformation_steps
        )

        PipelineService.validate_schedule(
            request.schedule_enabled,
            request.cron,
        )

        data = request.model_dump()

        if not request.schedule_enabled:
            data["cron"] = None

        pipeline = create_pipeline_document(
            owner_id=owner_id,
            data=data,
        )

        pipeline["status"] = (
            PipelineStatus.VALID.value
        )

        created = await PipelineRepository.create(
            pipeline
        )

        return PipelineService.format_pipeline(
            created
        )

    @staticmethod
    async def get_pipelines(
        user_id: str,
        role: str,
    ) -> list[dict]:

        owner_id = (
            None
            if role == "admin"
            else user_id
        )

        pipelines = (
            await PipelineRepository.find_all(
                owner_id=owner_id
            )
        )

        return [
            PipelineService.format_pipeline(
                pipeline
            )
            for pipeline in pipelines
        ]

    @staticmethod
    async def get_pipeline(
        pipeline_id: str,
        user_id: str,
        role: str,
    ) -> dict:

        pipeline = (
            await PipelineRepository.find_by_id(
                pipeline_id
            )
        )

        PipelineService.validate_access(
            pipeline,
            user_id,
            role,
        )

        return PipelineService.format_pipeline(
            pipeline
        )

    @staticmethod
    async def update_pipeline(
        pipeline_id: str,
        user_id: str,
        role: str,
        request,
    ) -> dict:

        pipeline = (
            await PipelineRepository.find_by_id(
                pipeline_id
            )
        )

        PipelineService.validate_access(
            pipeline,
            user_id,
            role,
        )

        updates = request.model_dump(
            exclude_unset=True
        )

        if not updates:
            return PipelineService.format_pipeline(
                pipeline
            )

        source = pipeline.get(
            "source",
            {},
        ).copy()

        destination = pipeline.get(
            "destination",
            {},
        ).copy()

        transformation = pipeline.get(
            "transformation",
            {},
        ).copy()

        schedule = pipeline.get(
            "schedule",
            {},
        ).copy()

        if "source_connection_id" in updates:

            await PipelineService.validate_connection(
                updates["source_connection_id"],
                user_id,
                role,
            )

            source["connection_id"] = updates.pop(
                "source_connection_id"
            )

        if "source_object_name" in updates:

            source["object_name"] = updates.pop(
                "source_object_name"
            )

        if "transformation_steps" in updates:

            steps = updates.pop(
                "transformation_steps"
            )

            PipelineService.validate_transformations(
                steps
            )

            transformation["steps"] = steps

        if "destination_connection_id" in updates:

            await PipelineService.validate_connection(
                updates["destination_connection_id"],
                user_id,
                role,
            )

            destination["connection_id"] = (
                updates.pop(
                    "destination_connection_id"
                )
            )

        if "destination_object_name" in updates:

            destination["object_name"] = updates.pop(
                "destination_object_name"
            )

        if "write_mode" in updates:

            destination["write_mode"] = (
                updates.pop("write_mode").value
            )

        if "schedule_enabled" in updates:

            schedule["enabled"] = updates.pop(
                "schedule_enabled"
            )

        if "cron" in updates:

            schedule["cron"] = updates.pop(
                "cron"
            )

        if not schedule.get(
            "enabled",
            False,
        ):
            schedule["cron"] = None

        PipelineService.validate_schedule(
            schedule_enabled=schedule.get(
                "enabled",
                False,
            ),
            cron=schedule.get("cron"),
        )

        updates["source"] = source

        updates["transformation"] = (
            transformation
        )

        updates["destination"] = destination

        updates["schedule"] = schedule

        updates["status"] = (
            PipelineStatus.VALID.value
        )

        updates["updated_at"] = (
            datetime.now(timezone.utc)
        )

        updated = await PipelineRepository.update(
            pipeline_id,
            updates,
        )

        return PipelineService.format_pipeline(
            updated
        )

    @staticmethod
    async def delete_pipeline(
        pipeline_id: str,
        user_id: str,
        role: str,
    ) -> None:

        pipeline = (
            await PipelineRepository.find_by_id(
                pipeline_id
            )
        )

        PipelineService.validate_access(
            pipeline,
            user_id,
            role,
        )

        await PipelineRepository.delete(
            pipeline_id
        )

    @staticmethod
    async def preview_pipeline(
        pipeline_id: str,
        user_id: str,
        role: str,
        limit: int = 20,
    ) -> dict:

        pipeline = (
            await PipelineRepository.find_by_id(
                pipeline_id
            )
        )

        PipelineService.validate_access(
            pipeline,
            user_id,
            role,
        )

        source_connection_id = pipeline[
            "source"
        ]["connection_id"]

        source_object_name = pipeline[
            "source"
        ]["object_name"]

        connection_request = (
            ConnectionActionRequest(
                action=ConnectionAction.PREVIEW,
                object_name=source_object_name,
                limit=limit,
            )
        )

        source_result = (
            await ConnectionService.perform_action(
                connection_id=source_connection_id,
                user_id=user_id,
                role=role,
                request=connection_request,
            )
        )

        source_rows = (
            source_result.data or []
        )

        steps = (
            pipeline.get(
                "transformation",
                {},
            ).get(
                "steps",
                [],
            )
        )

        PipelineService.validate_transformations(
            steps
        )

        transformation_previews = (
            SparkService.preview_steps(
                rows=source_rows,
                steps=steps,
                limit=limit,
            )
        )

        final_data = (
            transformation_previews[-1]["data"]
            if transformation_previews
            else source_rows[:limit]
        )

        return {
            "success": True,
            "message": (
                SuccessMessages.PIPELINE_PREVIEW_FETCHED
            ),
            "pipeline_id": pipeline_id,
            "source_data": source_rows[:limit],
            "transformation_steps": (
                transformation_previews
            ),
            "final_data": final_data,
        }

    @staticmethod
    def validate_access(
        pipeline: dict | None,
        user_id: str,
        role: str,
    ) -> None:

        if not pipeline:

            raise NotFoundException(
                ErrorMessages.PIPELINE_NOT_FOUND,
                error_code="PIPELINE_NOT_FOUND",
            )

        if (
            role != "admin"
            and pipeline["owner_id"] != user_id
        ):

            raise NotFoundException(
                ErrorMessages.PIPELINE_NOT_FOUND,
                error_code="PIPELINE_NOT_FOUND",
            )
