from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import os

print("Testing MongoDB connection...")
try:
    from pymongo import MongoClient
    client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
    client.server_info()
    db_name = os.getenv("MONGO_DB_NAME")
    print(f"Database name from .env: {db_name}")
    db = client[db_name]
    collection = db[os.getenv("MONGO_COLLECTION_NAME")]
    count = collection.count_documents({})
    print(f"MongoDB connected! (found {count} documents)")
except Exception as e:
    print(f"MongoDB connection FAILED: {e}")

print("\nTesting video collection...")
try:
    from pymongo import MongoClient
    client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
    db = client[os.getenv("MONGO_DB_NAME")]
    videos_collection = db[os.getenv("VIDEOS_COLLECTION_NAME", "videos")]
    count = videos_collection.count_documents({})
    print(f"Videos collection connected! (found {count} videos)")
except Exception as e:
    print(f"Videos collection check FAILED: {e}")