from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

with DAG(
    dag_id="dbt_cloud_run_job_create",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
) as dag:

    trigger_dbt_cloud_job_run = DbtCloudRunJobOperator(
        task_id="trigger_dbt_cloud_job_run",
        job_id=70471823548773,  # replace with your real job id
        dbt_cloud_conn_id="dbt_cloud_default",
    )
