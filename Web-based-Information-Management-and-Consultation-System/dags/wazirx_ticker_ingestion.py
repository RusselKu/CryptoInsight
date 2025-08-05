from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils.api_helpers import fetch_api_data
from utils.mongo_utils import get_raw_collection, get_processed_collection
import bson

DB_NAME = "project_db"
SOURCE_NAME = "wazirx_tickers"
API_URL = "https://api.wazirx.com/sapi/v1/tickers/24hr"

default_args = {
    "owner": "DamianNovelo",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=5)
}

def clean_object_ids(obj):
    """Remove ObjectId for XCom serialization."""
    if isinstance(obj, dict):
        return {k: clean_object_ids(v) for k, v in obj.items() if not isinstance(v, bson.ObjectId)}
    elif isinstance(obj, list):
        return [clean_object_ids(v) for v in obj]
    return obj

def extract_wazirx_data(ti):
    """Extract WazirX 24hr ticker data and store raw in MongoDB."""
    data = fetch_api_data(API_URL)
    if not data or not isinstance(data, list):
        raise ValueError("Invalid or empty response from WazirX API.")

    collection = get_raw_collection(DB_NAME, SOURCE_NAME)
    record = {
        "data": data,
        "timestamp": datetime.utcnow(),
        "source": "WazirX API",
        "metadata": {
            "num_records": len(data),
            "status": "raw"
        }
    }
    collection.insert_one(record)
    ti.xcom_push(key="num_records", value=len(data))

def transform_wazirx_data(ti):
    """Transform raw WazirX data into structured format for analysis."""
    raw_collection = get_raw_collection(DB_NAME, SOURCE_NAME)
    processed_collection = get_processed_collection(DB_NAME, SOURCE_NAME)

    latest = raw_collection.find_one(sort=[("_id", -1)])
    if not latest or "data" not in latest:
        raise ValueError("No valid raw WazirX data found for transformation.")

    raw_data = latest["data"]
    transformed = []

    for ticker in raw_data:
        transformed.append({
            "symbol": ticker.get("symbol"),
            "base_asset": ticker.get("baseAsset"),
            "quote_asset": ticker.get("quoteAsset"),
            "open_price": float(ticker.get("openPrice", 0)),
            "last_price": float(ticker.get("lastPrice", 0)),
            "high_price": float(ticker.get("highPrice", 0)),
            "low_price": float(ticker.get("lowPrice", 0)),
            "volume": float(ticker.get("volume", 0)),
            "bid_price": float(ticker.get("bidPrice", 0)),
            "ask_price": float(ticker.get("askPrice", 0)),
            "timestamp": datetime.utcfromtimestamp(ticker.get("at", 0) / 1000).isoformat() if ticker.get("at") else None
        })

    # Filter active pairs (volume > 0)
    active_pairs = [t for t in transformed if t["volume"] > 0]
    most_active = max(active_pairs, key=lambda x: x["volume"], default=None)

    processed_record = {
        "wazirx_data": transformed,
        "metadata": {
            "processed_at": datetime.utcnow().isoformat(),
            "total_pairs": len(transformed),
            "active_pairs": len(active_pairs),
            "most_active": most_active["symbol"] if most_active else None
        }
    }

    processed_collection.insert_one(processed_record)
    ti.xcom_push(key="transformed_data", value=clean_object_ids(processed_record))

with DAG(
    "wazirx_ticker_ingestion",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "crypto", "wazirx"]
) as dag:

    extract = PythonOperator(
        task_id="extract_wazirx_data",
        python_callable=extract_wazirx_data
    )

    transform = PythonOperator(
        task_id="transform_wazirx_data",
        python_callable=transform_wazirx_data
    )

    extract >> transform
