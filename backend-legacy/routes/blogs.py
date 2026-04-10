from fastapi import APIRouter, HTTPException
from models.schemas import BlogCreate, BlogResponse
from services import mongo_service

router = APIRouter(prefix="/blogs", tags=["blogs"])


@router.get("", response_model=list[BlogResponse])
async def get_blogs():
    try:
        return mongo_service.get_all_blogs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=BlogResponse)
async def create_blog(blog: BlogCreate):
    try:
        blog_data = blog.model_dump()
        return mongo_service.create_blog(blog_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{blog_id}")
async def delete_blog(blog_id: str):
    try:
        deleted = mongo_service.delete_blog(blog_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Blog not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
