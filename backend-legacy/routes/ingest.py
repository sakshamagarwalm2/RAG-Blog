from fastapi import APIRouter
from models.schemas import IngestResponse
from services import mongo_service, embeddings_service, faiss_service

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
async def ingest():
    blogs = mongo_service.get_all_blogs()
    videos = mongo_service.get_all_videos()
    
    def embed_with_progress(text: str) -> list[float]:
        return embeddings_service.embed_text(text)
    
    result = faiss_service.build_index(blogs, videos, embed_with_progress)
    
    return IngestResponse(
        status="success",
        blogs_indexed=result["blogs"],
        chunks_created=result["total_chunks"]
    )
