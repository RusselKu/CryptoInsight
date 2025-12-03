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

def get_historical_binance_data(symbol):
    """Fetch historical data for a specific symbol from Binance tickers."""
    query = {"binance_data.symbol": symbol}
    projection = {"_id": 0, "metadata.processed_at": 1, "binance_data.$": 1}
    cursor = db["processed_binance_tickers"].find(query, projection).sort("metadata.processed_at", 1)
    
    historical_data = []
    for doc in cursor:
        data_point = doc['binance_data'][0]
        data_point['timestamp'] = doc['metadata']['processed_at']
        historical_data.append(data_point)
        
    return historical_data

def get_historical_wazirx_data(symbol):
    """Fetch historical data for a specific symbol from WazirX tickers."""
    query = {"wazirx_data.symbol": symbol}
    projection = {"_id": 0, "metadata.processed_at": 1, "wazirx_data.$": 1}
    cursor = db["processed_wazirx_tickers"].find(query, projection).sort("metadata.processed_at", 1)
    
    historical_data = []
    for doc in cursor:
        data_point = doc['wazirx_data'][0]
        data_point['timestamp'] = doc['metadata']['processed_at']
        historical_data.append(data_point)
        
    return historical_data
