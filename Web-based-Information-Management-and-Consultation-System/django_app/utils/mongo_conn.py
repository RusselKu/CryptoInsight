from pymongo import MongoClient
import os

# ✅ MongoDB connection
# CAMBIO IMPORTANTE AQUÍ ABAJO: Cambiamos 'mongodb' por 'localhost'
# Nota: Si instalaste MongoDB en Windows sin contraseña, usa la segunda opción comentada.

# OPCIÓN 1: Si usas Docker Desktop corriendo en tu PC (con usuario root y pass example):
#mongo_uri = os.getenv('MONGO_URI', 'mongodb://root:example@localhost:27017/project_db?authSource=admin')

# OPCIÓN 2: Si instalaste MongoDB Community Server directamente en Windows (sin usuario):
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/project_db')

client = MongoClient(mongo_uri)
db = client.get_database()  # Uses DB from URI (project_db)

# ✅ Functions to fetch processed data
def get_crypto_market_data():
    """Fetch latest processed cryptocurrency market data."""
    # Agregamos try/except para que no truene si la DB está vacía o apagada
    try:
        return list(db["processed_crypto_market"].find({}, {"_id": 0}).sort("_id", -1).limit(1))
    except Exception as e:
        print(f"Error conectando a Mongo: {e}")
        return []

def get_binance_tickers():
    """Fetch latest processed Binance tickers data."""
    try:
        return list(db["processed_binance_tickers"].find({}, {"_id": 0}).sort("_id", -1).limit(1))
    except:
        return []

def get_wazirx_tickers():
    """Fetch latest processed WazirX tickers data."""
    try:
        return list(db["processed_wazirx_tickers"].find({}, {"_id": 0}).sort("_id", -1).limit(1))
    except:
        return []

def get_historical_binance_data(symbol):
    """Fetch historical data for a specific symbol from Binance tickers."""
    try:
        query = {"binance_data.symbol": symbol}
        projection = {"_id": 0, "metadata.processed_at": 1, "binance_data.$": 1}
        cursor = db["processed_binance_tickers"].find(query, projection).sort("metadata.processed_at", 1)
        
        historical_data = []
        for doc in cursor:
            if 'binance_data' in doc and len(doc['binance_data']) > 0:
                data_point = doc['binance_data'][0]
                data_point['timestamp'] = doc['metadata']['processed_at']
                historical_data.append(data_point)
            
        return historical_data
    except:
        return []

def get_historical_wazirx_data(symbol):
    """Fetch historical data for a specific symbol from WazirX tickers."""
    try:
        query = {"wazirx_data.symbol": symbol}
        projection = {"_id": 0, "metadata.processed_at": 1, "wazirx_data.$": 1}
        cursor = db["processed_wazirx_tickers"].find(query, projection).sort("metadata.processed_at", 1)
        
        historical_data = []
        for doc in cursor:
            if 'wazirx_data' in doc and len(doc['wazirx_data']) > 0:
                data_point = doc['wazirx_data'][0]
                data_point['timestamp'] = doc['metadata']['processed_at']
                historical_data.append(data_point)
            
        return historical_data
    except:
        return []