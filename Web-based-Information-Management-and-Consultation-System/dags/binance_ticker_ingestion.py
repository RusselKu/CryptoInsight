from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils.api_helpers import fetch_api_data
from utils.mongo_utils import get_raw_collection, get_processed_collection
import bson

DB_NAME = "project_db"
SOURCE_NAME = "binance_tickers"
API_URL = "https://api4.binance.com/api/v3/ticker/24hr"

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

def extract_binance_data(ti):
    """Extract Binance 24hr ticker data and store raw in MongoDB."""
    data = fetch_api_data(API_URL)
    if not data or not isinstance(data, list):
        raise ValueError("Invalid or empty response from Binance API.")

    collection = get_raw_collection(DB_NAME, SOURCE_NAME)
    record = {
        "data": data,
        "timestamp": datetime.utcnow(),
        "source": "Binance API",
        "metadata": {
            "num_records": len(data),
            "status": "raw"
        }
    }
    collection.insert_one(record)
    ti.xcom_push(key="num_records", value=len(data))

def transform_binance_data(ti):
    """Transform raw Binance data into structured format for analysis."""
    raw_collection = get_raw_collection(DB_NAME, SOURCE_NAME)
    processed_collection = get_processed_collection(DB_NAME, SOURCE_NAME)

    latest = raw_collection.find_one(sort=[("_id", -1)])
    if not latest or "data" not in latest:
        raise ValueError("No valid raw Binance data found for transformation.")

    raw_data = latest["data"]
    transformed = []

    for ticker in raw_data:
        transformed.append({
            "symbol": ticker.get("symbol"),
            "price_change": float(ticker.get("priceChange", 0)),
            "price_change_percent": float(ticker.get("priceChangePercent", 0)),
            "last_price": float(ticker.get("lastPrice", 0)),
            "open_price": float(ticker.get("openPrice", 0)),
            "high_price": float(ticker.get("highPrice", 0)),
            "low_price": float(ticker.get("lowPrice", 0)),
            "bid_price": float(ticker.get("bidPrice", 0)),
            "bid_qty": float(ticker.get("bidQty", 0)),
            "ask_price": float(ticker.get("askPrice", 0)),
            "ask_qty": float(ticker.get("askQty", 0)),
            "volume_base": float(ticker.get("volume", 0)),
            "volume_quote": float(ticker.get("quoteVolume", 0)),
            "trade_count": ticker.get("count"),
            "open_time": datetime.utcfromtimestamp(ticker.get("openTime", 0) / 1000).isoformat() if ticker.get("openTime") else None,
            "close_time": datetime.utcfromtimestamp(ticker.get("closeTime", 0) / 1000).isoformat() if ticker.get("closeTime") else None
        })

    # Identify most traded pair
    most_traded = max(transformed, key=lambda x: x["volume_base"], default=None)

    processed_record = {
        "binance_data": transformed,
        "metadata": {
            "processed_at": datetime.utcnow().isoformat(),
            "total_pairs": len(transformed),
            "most_traded": most_traded["symbol"] if most_traded else None
        }
    }

    processed_collection.insert_one(processed_record)
    ti.xcom_push(key="transformed_data", value=clean_object_ids(processed_record))

with DAG(
    "binance_ticker_ingestion",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "crypto", "binance"]
) as dag:

    extract = PythonOperator(
        task_id="extract_binance_data",
        python_callable=extract_binance_data
    )

    transform = PythonOperator(
        task_id="transform_binance_data",
        python_callable=transform_binance_data
    )

    extract >> transform
