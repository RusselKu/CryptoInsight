from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'retrain_crypto_prediction_model',
    default_args=default_args,
    description='Retrains the cryptocurrency price prediction model daily.',
    schedule_interval=timedelta(days=1), # Run once every day
    start_date=datetime(2025, 12, 1),
    catchup=False,
    tags=['predictions', 'ml'],
) as dag:
    retrain_task = BashOperator(
        task_id='retrain_model',
        bash_command='docker exec web-based-information-management-and-consultation-system-django-1 python /app/predictions/train_model.py',
    )

    retrain_binance_task = BashOperator(
        task_id='retrain_binance_model',
        bash_command='docker exec web-based-information-management-and-consultation-system-django-1 python /app/predictions/train_binance.py',
    )

    retrain_wazirx_task = BashOperator(
        task_id='retrain_wazirx_model',
        bash_command='docker exec web-based-information-management-and-consultation-system-django-1 python /app/predictions/train_wazirx.py',
    )

    [retrain_task, retrain_binance_task, retrain_wazirx_task]
