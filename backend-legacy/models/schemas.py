from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BlogCreate(BaseModel):
    title: str
    content: str
    url: str
    tags: list[str] = []
    summary: Optional[str] = None


class BlogResponse(BaseModel):
    id: str
    title: str
    content: str
    url: str
    tags: list[str]
    summary: Optional[str]
    created_at: datetime


class VideoCreate(BaseModel):
    youtube_url: str
    tags: list[str] = []


class VideoResponse(BaseModel):
    id: str
    youtube_url: str
    video_id: str
    title: str
    channel: str
    thumbnail_url: str
    transcript_word_count: int
    was_summarized: bool
    tags: list[str]
    created_at: datetime


class ChatRequest(BaseModel):
    query: str
    chat_history: list[dict] = Field(default_factory=list)


class SourceItem(BaseModel):
    title: str
    url: str
    source_type: str
    thumbnail_url: Optional[str] = None
    video_id: Optional[str] = None
    channel: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    chunks_used: int


class IngestResponse(BaseModel):
    status: str
    blogs_indexed: int
    chunks_created: int
