from datetime import datetime
from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

# ===== CONFIG =====
DBT_CLOUD_CONN_ID = "dbt_cloud_default"
ACCOUNT_ID = 70471823522439
JOB_ID = 123456789  # <-- PUT YOUR REAL JOB ID HERE (number only)
# ==================

default_args = {
    "owner": "airflow",
}

with DAG(
    dag_id="dbt_cloud_run_job_create",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    trigger_dbt_cloud_job_run = DbtCloudRunJobOperator(
        task_id="trigger_dbt_cloud_job_run",
        job_id=JOB_ID,
        dbt_cloud_conn_id=DBT_CLOUD_CONN_ID,
        account_id=ACCOUNT_ID,
        check_interval=10,
        timeout=300,
    )
