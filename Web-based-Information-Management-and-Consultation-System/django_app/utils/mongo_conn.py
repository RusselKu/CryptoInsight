from pymongo import MongoClient
import os

# ✅ MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://root:example@mongodb:27017/project_db?authSource=admin')
client = MongoClient(mongo_uri)
db = client.get_database()  # Uses DB from URI (project_db)

# ✅ Functions to fetch processed data
def get_crypto_market_data():
    """Fetch latest processed cryptocurrency market data."""
    return list(db["processed_crypto_market"].find({}, {"_id": 0}).sort("_id", -1).limit(1))

def get_binance_tickers():
    """Fetch latest processed Binance tickers data."""
    return list(db["processed_binance_tickers"].find({}, {"_id": 0}).sort("_id", -1).limit(1))

def get_wazirx_tickers():
    """Fetch latest processed WazirX tickers data."""
    return list(db["processed_wazirx_tickers"].find({}, {"_id": 0}).sort("_id", -1).limit(1))
