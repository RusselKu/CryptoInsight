from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils.api_helpers import fetch_api_data
from utils.mongo_utils import get_raw_collection, get_processed_collection
import bson

DB_NAME = "project_db"
SOURCE_NAME = "crypto_market"
API_URL = "https://api.coingecko.com/api/v3/coins/markets"
API_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": "false"
}

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

def extract_crypto_data(ti):
    """Extract cryptocurrency data from API and store raw in MongoDB."""
    data = fetch_api_data(API_URL, params=API_PARAMS)
    if not data or not isinstance(data, list):
        raise ValueError("Invalid or empty API response for crypto data.")

    collection = get_raw_collection(DB_NAME, SOURCE_NAME)
    record = {
        "data": data,
        "timestamp": datetime.utcnow(),
        "source": "CoinGecko API",
        "metadata": {
            "num_records": len(data),
            "currency": "USD",
            "status": "raw"
        }
    }
    collection.insert_one(record)
    ti.xcom_push(key="num_records", value=len(data))

def transform_crypto_data(ti):
    """Transform raw crypto data into structured format for analysis."""
    raw_collection = get_raw_collection(DB_NAME, SOURCE_NAME)
    processed_collection = get_processed_collection(DB_NAME, SOURCE_NAME)

    latest = raw_collection.find_one(sort=[("_id", -1)])
    if not latest or "data" not in latest:
        raise ValueError("No valid raw crypto data found for transformation.")

    raw_data = latest["data"]
    transformed = []

    for coin in raw_data:
        transformed.append({
            "id": coin.get("id"),
            "symbol": coin.get("symbol"),
            "name": coin.get("name"),
            "image": coin.get("image"),
            "current_price": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "fully_diluted_valuation": coin.get("fully_diluted_valuation"),
            "total_volume": coin.get("total_volume"),
            "price_change_24h": coin.get("price_change_24h"),
            "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
            "high_24h": coin.get("high_24h"),
            "low_24h": coin.get("low_24h"),
            "circulating_supply": coin.get("circulating_supply"),
            "total_supply": coin.get("total_supply"),
            "max_supply": coin.get("max_supply"),
            "ath": coin.get("ath"),
            "ath_date": coin.get("ath_date"),
            "atl": coin.get("atl"),
            "atl_date": coin.get("atl_date")
        })

    processed_record = {
        "crypto_data": transformed,
        "metadata": {
            "processed_at": datetime.utcnow().isoformat(),
            "total_coins": len(transformed),
            "top_coin": raw_data[0].get("name") if raw_data else None
        }
    }

    processed_collection.insert_one(processed_record)
    ti.xcom_push(key="transformed_data", value=clean_object_ids(processed_record))

with DAG(
    "cryptocurrencymarket",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "crypto"]
) as dag:

    extract = PythonOperator(
        task_id="extract_crypto_data",
        python_callable=extract_crypto_data
    )

    transform = PythonOperator(
        task_id="transform_crypto_data",
        python_callable=transform_crypto_data
    )

    extract >> transform
