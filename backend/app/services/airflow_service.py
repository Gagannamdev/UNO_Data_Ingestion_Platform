from pathlib import Path


class AirflowService:

    @staticmethod
    def get_dags_directory() -> Path:
        """
        Returns the Airflow DAGs folder.

        Project structure:

        UNO_Data_Ingestion_Platform/
        ├── backend/
        └── airflow/
            └── dags/
        """

        backend_directory = (
            Path(__file__)
            .resolve()
            .parents[2]
        )

        project_directory = (
            backend_directory.parent
        )

        dags_directory = (
            project_directory
            / "airflow"
            / "dags"
            / "generated"
        )

        dags_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return dags_directory

    @staticmethod
    def get_dag_id(
        pipeline_id: str,
    ) -> str:
        return f"uno_pipeline_{pipeline_id}"

    @staticmethod
    def get_dag_file(
        pipeline_id: str,
    ) -> Path:

        return (
            AirflowService
            .get_dags_directory()
            / f"uno_pipeline_{pipeline_id}.py"
        )

    @staticmethod
    def create_dag(
        pipeline_id: str,
        cron: str,
    ) -> dict:

        dag_id = (
            AirflowService
            .get_dag_id(pipeline_id)
        )

        dag_file = (
            AirflowService
            .get_dag_file(pipeline_id)
        )

        dag_code = f'''
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


PIPELINE_ID = "{pipeline_id}"


def execute_pipeline():

    print(
        f"Starting UNO pipeline: {{PIPELINE_ID}}"
    )
 

    print(
        f"UNO pipeline {{PIPELINE_ID}} completed"
    )


with DAG(
    dag_id="{dag_id}",
    start_date=datetime(2026, 1, 1),
    schedule="{cron}",
    catchup=False,
    tags=[
        "UNO",
        "Data Ingestion",
    ],
) as dag:

    run_pipeline = PythonOperator(
        task_id="execute_pipeline",
        python_callable=execute_pipeline,
    )
'''

        dag_file.write_text(
            dag_code,
            encoding="utf-8",
        )

        return {
            "success": True,
            "dag_id": dag_id,
            "dag_file": str(dag_file),
            "message": (
                "Airflow DAG created successfully"
            ),
        }

    @staticmethod
    def delete_dag(
        pipeline_id: str,
    ) -> dict:

        dag_file = (
            AirflowService
            .get_dag_file(pipeline_id)
        )

        if dag_file.exists():
            dag_file.unlink()

        return {
            "success": True,
            "dag_id": (
                AirflowService
                .get_dag_id(pipeline_id)
            ),
            "message": (
                "Airflow DAG deleted successfully"
            ),
        }
