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


class ChatRequest(BaseModel):
    query: str
    chat_history: list[dict] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    chunks_used: int


class IngestResponse(BaseModel):
    status: str
    blogs_indexed: int
    chunks_created: int
