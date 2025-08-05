from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "DamianNovelo",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="main_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["orchestration", "crypto", "pipeline"]
) as dag:

    def log_start():
        print("🚀 Main pipeline started.")

    start_task = PythonOperator(
        task_id="start_pipeline",
        python_callable=log_start
    )

    trigger_coingecko = TriggerDagRunOperator(
        task_id="trigger_cryptocurrencymarket_dag",
        trigger_dag_id="cryptocurrencymarket"  # ✅ Correct name
    )

    trigger_binance = TriggerDagRunOperator(
        task_id="trigger_binance_dag",
        trigger_dag_id="binance_ticker_ingestion"
    )

    trigger_wazirx = TriggerDagRunOperator(
        task_id="trigger_wazirx_dag",
        trigger_dag_id="wazirx_ticker_ingestion"
    )

    trigger_load_mongo = TriggerDagRunOperator(
        task_id="trigger_load_mongo_dag",
        trigger_dag_id="load_mongo"
    )

    # Define execution order
    start_task >> trigger_coingecko >> trigger_binance >> trigger_wazirx >> trigger_load_mongo
