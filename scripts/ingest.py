import sys
from pathlib import Path

if sys.prefix == sys.base_prefix:
    print("ERROR: venv not activated. Run: source venv/bin/activate")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Add the legacy backend to path so we can import its services
legacy_path = str(Path(__file__).parent.parent / "backend-legacy")
if legacy_path not in sys.path:
    sys.path.insert(0, legacy_path)

from services import mongo_service, embeddings_service, faiss_service

blogs = mongo_service.get_all_blogs()
print(f"Found {len(blogs)} blogs in MongoDB")

videos = mongo_service.get_all_videos()
print(f"Found {len(videos)} videos in MongoDB")

if not blogs and not videos:
    print("Nothing to index. Add blogs via Blog Manager or videos via Video Manager.")
    sys.exit(0)

def embed_with_progress(text: str) -> list[float]:
    return embeddings_service.embed_text(text)

print("Building FAISS index for blogs + videos...")
result = faiss_service.build_index(blogs, videos, embed_with_progress)
print(f"\nIndex built:")
print(f"  Blogs:        {result['blogs']} indexed")
print(f"  Videos:       {result['videos']} indexed")
print(f"  Total chunks: {result['total_chunks']}")
print(f"  Saved to:     faiss_index/")
print("\nRe-index complete. Chat will now search both blogs and videos.")
