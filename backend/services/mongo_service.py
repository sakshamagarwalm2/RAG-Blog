import os
from datetime import datetime
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

_MONGO_URI = os.getenv("MONGO_URI")
_MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
_MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

if not all([_MONGO_URI, _MONGO_DB_NAME, _MONGO_COLLECTION_NAME]):
    raise RuntimeError("MongoDB configuration missing. Check .env file.")

_client: Optional[MongoClient] = None


def _get_client() -> MongoClient:
    global _client
    if _client is None:
        try:
            _client = MongoClient(_MONGO_URI, serverSelectionTimeoutMS=5000)
            _client.server_info()
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            raise RuntimeError(f"MongoDB connection failed: {e}")
    return _client


def _get_collection():
    client = _get_client()
    return client[_MONGO_DB_NAME][_MONGO_COLLECTION_NAME]


def _serialize_doc(doc: dict) -> dict:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    if "created_at" in doc and isinstance(doc["created_at"], datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc


def get_all_blogs() -> list[dict]:
    collection = _get_collection()
    cursor = collection.find().sort("created_at", -1)
    return [_serialize_doc(doc) for doc in cursor]


def get_blog_by_id(blog_id: str) -> Optional[dict]:
    from bson import ObjectId
    collection = _get_collection()
    doc = collection.find_one({"_id": ObjectId(blog_id)})
    return _serialize_doc(doc) if doc else None


def create_blog(blog_data: dict) -> dict:
    blog_data["created_at"] = datetime.utcnow()
    collection = _get_collection()
    result = collection.insert_one(blog_data)
    doc = collection.find_one({"_id": result.inserted_id})
    return _serialize_doc(doc)


def delete_blog(blog_id: str) -> bool:
    from bson import ObjectId
    collection = _get_collection()
    result = collection.delete_one({"_id": ObjectId(blog_id)})
    return result.deleted_count > 0


def get_blogs_count() -> int:
    collection = _get_collection()
    return collection.count_documents({})
