import sys
from pathlib import Path

if sys.prefix == sys.base_prefix:
    print("ERROR: venv not activated. Run: source venv/bin/activate")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services import mongo_service, embeddings_service, faiss_service

print("Fetching blogs from MongoDB...")
blogs = mongo_service.get_all_blogs()
print(f"Found {len(blogs)} blogs in MongoDB")

if not blogs:
    print("No blogs found. Add blogs first using the Blog Manager UI.")
    sys.exit(0)

def embed_with_progress(text: str) -> list[float]:
    return embeddings_service.embed_text(text)

print("Building FAISS index...")
blogs_count, chunks_count = faiss_service.build_index(blogs, embed_with_progress)
print(f"\nIndex built: {blogs_count} blogs, {chunks_count} chunks — saved to faiss_index/")
