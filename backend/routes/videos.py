from fastapi import APIRouter, HTTPException
from backend.services import mongo_service, youtube_service
from backend.models.schemas import VideoCreate, VideoResponse
from pydantic import BaseModel
import google.generativeai as genai
import os

router = APIRouter(prefix="/videos", tags=["videos"])


class VideoManualCreate(BaseModel):
    youtube_url: str
    transcript_raw: str
    tags: list[str] = []


@router.get("", response_model=list[VideoResponse])
def get_videos():
    return mongo_service.get_all_videos()


@router.post("", response_model=VideoResponse)
def add_video(payload: VideoCreate):
    try:
        video_id = youtube_service.extract_video_id(payload.youtube_url)
        if mongo_service.video_exists(video_id):
            raise HTTPException(status_code=409, detail="This video has already been added.")
        
        video_data = youtube_service.process_youtube_url(payload.youtube_url, payload.tags)
        
        saved = mongo_service.create_video(video_data)
        return saved
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")


@router.post("/manual", response_model=VideoResponse)
def add_video_manual(payload: VideoManualCreate):
    """Add video with manually provided transcript"""
    try:
        video_id = youtube_service.extract_video_id(payload.youtube_url)
        if mongo_service.video_exists(video_id):
            raise HTTPException(status_code=409, detail="This video has already been added.")
        
        metadata = youtube_service.get_video_metadata(video_id)
        transcript_text = payload.transcript_raw.strip()
        word_count = len(transcript_text.split())
        
        GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        MAX_WORDS = int(os.getenv("VIDEO_SUMMARY_MAX_WORDS", 3000))
        
        if word_count > MAX_WORDS:
            summary = youtube_service.summarize_transcript(transcript_text, metadata["title"])
            was_summarized = True
        else:
            summary = transcript_text
            was_summarized = False
        
        video_data = {
            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
            "video_id": video_id,
            "title": metadata["title"],
            "channel": metadata["channel"],
            "thumbnail_url": metadata["thumbnail_url"],
            "transcript_raw": transcript_text,
            "transcript_word_count": word_count,
            "summary": summary,
            "was_summarized": was_summarized,
            "tags": payload.tags,
        }
        
        saved = mongo_service.create_video(video_data)
        return saved
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")


@router.delete("/{video_id}")
def delete_video(video_id: str):
    deleted = mongo_service.delete_video(video_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"deleted": True}