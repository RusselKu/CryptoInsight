import pandas as pd
from pymongo import MongoClient

# MongoDB connection details
MONGO_DB_NAME = 'project_db'
MONGO_HOST = 'mongodb://root:example@mongodb:27017/'

def load_binance_data_to_dataframe():
    """
    Loads data from the 'processed_binance_tickers' collection into a pandas DataFrame using pymongo.
    """
    print("Connecting to MongoDB with pymongo...")
    try:
        client = MongoClient(MONGO_HOST, authSource='admin')
        db = client[MONGO_DB_NAME]
        
        print("Loading data from 'processed_binance_tickers' collection...")
        market_data_doc = db.processed_binance_tickers.find_one(sort=[("_id", -1)])
        
        if market_data_doc and 'binance_data' in market_data_doc:
            coin_list = market_data_doc['binance_data']
            df = pd.DataFrame(coin_list)
            print(f"Successfully loaded {len(df)} records from the nested document.")
            return df
        else:
            print("No document found or document is malformed in 'processed_binance_tickers' collection.")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error loading data with pymongo: {e}")
        return pd.DataFrame()
    finally:
        if 'client' in locals() and client:
            client.close()
            print("MongoDB connection closed.")
