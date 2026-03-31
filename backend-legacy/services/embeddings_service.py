import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")

if not _GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env file")

genai.configure(api_key=_GEMINI_API_KEY)


def embed_text(text: str) -> list[float]:
    for attempt in range(3):
        try:
            result = genai.embed_content(
                model=_EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
            else:
                raise ValueError(f"Embedding failed after 3 attempts: {e}")
    return []


def embed_query(text: str) -> list[float]:
    for attempt in range(3):
        try:
            result = genai.embed_content(
                model=_EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_query"
            )
            return result["embedding"]
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
            else:
                raise ValueError(f"Query embedding failed after 3 attempts: {e}")
    return []
