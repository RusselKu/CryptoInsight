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
        # Command to execute the train_model.py script inside the Django container
        # Note: This assumes the Django container is running and accessible
        # The /app/predictions/train_model.py path is relative to the Django container's WORKDIR
        bash_command='docker exec web-based-information-management-and-consultation-system-django-1 python /app/predictions/train_model.py',
    )
