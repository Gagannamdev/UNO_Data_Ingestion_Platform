from datetime import datetime, timezone
from typing import Optional

from app.enums.pipeline_enum import PipelineStatus


def create_pipeline_document(
    owner_id: str,
    data: dict,
) -> dict:
    now = datetime.now(timezone.utc)

    return {
        "owner_id": owner_id,
        "pipeline_name": data["pipeline_name"],
        "description": data.get("description"),

        "source": {
            "connection_id": data["source_connection_id"],
            "object_name": data["source_object_name"],
        },

        "transformation": {
            "steps": data.get("transformation_steps", []),
        },

        "destination": {
            "connection_id": data["destination_connection_id"],
            "object_name": data["destination_object_name"],
            "write_mode": data["write_mode"].value,
        },

        "schedule": {
            "enabled": data.get("schedule_enabled", False),
            "cron": data.get("cron"),
        },

        "status": PipelineStatus.INVALID.value,
        "last_run_status": None,
        "last_run_at": None,

        "created_at": now,
        "updated_at": now,
    }
