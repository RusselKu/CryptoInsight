from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

default_args = {
    "owner": "DamianNovelo",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

def load_consolidated_data():
    """Reads processed data from multiple Mongo collections and consolidates into one."""
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb://root:example@mongodb:27017/project_db?authSource=admin"
    )
    client = MongoClient(mongo_uri)
    db = client.get_database()

    # Collections to consolidate
    crypto_data = db["processed_crypto_market"].find_one(sort=[("_id", -1)])
    binance_data = db["processed_binance_tickers"].find_one(sort=[("_id", -1)])
    wazirx_data = db["processed_wazirx_tickers"].find_one(sort=[("_id", -1)])

    consolidated = {
        "crypto_market": crypto_data.get("crypto_data", []) if crypto_data else [],
        "binance": binance_data.get("binance_data", []) if binance_data else [],
        "wazirx": wazirx_data.get("wazirx_data", []) if wazirx_data else [],
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "total_sources": 3,
            "status": "consolidated",
            "sources": ["CoinGecko", "Binance", "WazirX"]
        }
    }

    # Insert into consolidated collection
    consolidated_collection = db["consolidated_crypto_dashboard"]
    consolidated_collection.insert_one(consolidated)

    print("✅ Consolidated data inserted into 'consolidated_crypto_dashboard'")

with DAG(
    "load_mongo",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "mongo", "consolidation"]
) as dag:

    consolidate_task = PythonOperator(
        task_id="consolidate_processed_data",
        python_callable=load_consolidated_data
    )
