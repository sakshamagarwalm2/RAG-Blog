from fastapi import APIRouter
from backend.models.schemas import IngestResponse
from backend.services import mongo_service, embeddings_service, faiss_service

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
async def ingest():
    blogs = mongo_service.get_all_blogs()
    
    def embed_with_progress(text: str) -> list[float]:
        return embeddings_service.embed_text(text)
    
    blogs_count, chunks_count = faiss_service.build_index(blogs, embed_with_progress)
    
    return IngestResponse(
        status="success",
        blogs_indexed=blogs_count,
        chunks_created=chunks_count
    )
