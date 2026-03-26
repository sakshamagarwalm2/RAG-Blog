import sys
from pathlib import Path

if sys.prefix == sys.base_prefix:
    print("ERROR: Virtual environment is not activated.")
    print("Run: source venv/bin/activate  (macOS/Linux)")
    print("Run: venv\\Scripts\\activate.bat  (Windows)")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import os

print("Testing MongoDB connection...")
try:
    from pymongo import MongoClient
    client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client[os.getenv("MONGO_DB_NAME")]
    collection = db[os.getenv("MONGO_COLLECTION_NAME")]
    count = collection.count_documents({})
    print(f"MongoDB connected ✓  (found {count} documents)")
except Exception as e:
    print(f"MongoDB connection FAILED ✗  {e}")

print("\nTesting Gemini API connection...")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    result = genai.embed_content(
        model=os.getenv("EMBEDDING_MODEL"),
        content="test",
        task_type="retrieval_document"
    )
    dim = len(result["embedding"])
    print(f"Gemini API connected ✓  (embedding dim: {dim})")
except Exception as e:
    print(f"Gemini API FAILED ✗  {e}")

print("\nTesting video collection...")
try:
    from pymongo import MongoClient
    client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
    db = client[os.getenv("MONGO_DB_NAME")]
    videos_collection = db[os.getenv("VIDEOS_COLLECTION_NAME", "videos")]
    count = videos_collection.count_documents({})
    print(f"Videos collection connected ✓  (found {count} videos)")
except Exception as e:
    print(f"Videos collection check FAILED ✗  {e}")

print("\nTesting youtube-transcript-api...")
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("youtube-transcript-api installed ✓")
except ImportError:
    print("youtube-transcript-api NOT installed ✗  Run: pip install youtube-transcript-api")

print("\nTesting pytube...")
try:
    import pytube
    print("pytube installed ✓")
except ImportError:
    print("pytube NOT installed ✗  Run: pip install pytube")
