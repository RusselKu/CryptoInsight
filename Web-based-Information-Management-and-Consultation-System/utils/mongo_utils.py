from pymongo import MongoClient
from urllib.parse import quote_plus
import os

_client = None  # Cache for MongoClient

def get_mongo_client():
    """Return a MongoDB client (singleton pattern for performance)."""
    global _client
    if _client:
        return _client

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        username = quote_plus("root")
        password = quote_plus("example")
        mongo_uri = f"mongodb://{username}:{password}@mongodb:27017/?authSource=admin"
    
    try:
        _client = MongoClient(mongo_uri)
        # Test connection
        _client.admin.command("ping")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    return _client

def get_raw_collection(db_name: str, source_name: str):
    return get_mongo_client()[db_name][f"raw_{source_name.lower()}"]

def get_processed_collection(db_name: str, source_name: str):
    return get_mongo_client()[db_name][f"processed_{source_name.lower()}"]

def insert_data(collection, data):
    """Insert a document or list of documents into a collection."""
    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)

def find_latest(collection):
    """Find the latest document based on _id."""
    return collection.find_one(sort=[("_id", -1)])
