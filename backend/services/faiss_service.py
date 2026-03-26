import os
import json
import numpy as np
import faiss
from typing import Callable, Tuple, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")
_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
_VIDEO_CHUNK_SIZE = int(os.getenv("VIDEO_CHUNK_SIZE", "600"))
_VIDEO_CHUNK_OVERLAP = int(os.getenv("VIDEO_CHUNK_OVERLAP", "80"))
_TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))


def chunk_text(text: str, size: int = _CHUNK_SIZE, overlap: int = _CHUNK_OVERLAP) -> list[str]:
    chunks = []
    if not text or len(text) < 50:
        return chunks
    
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        
        if len(chunk) >= 50:
            chunks.append(chunk)
        
        if end >= len(text):
            break
        
        start = end - overlap
    
    return chunks


def _normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def build_index(blogs: list[dict], videos: list[dict], embed_fn: Callable[[str], list[float]]) -> dict:
    Path(_FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)
    
    all_chunks = []
    all_metadata = []
    
    for blog in blogs:
        content = blog.get("content", "")
        chunks = chunk_text(content)
        
        for chunk_idx, chunk_content in enumerate(chunks):
            embedding = embed_fn(chunk_content)
            all_chunks.append(embedding)
            all_metadata.append({
                "source_type": "blog",
                "source_id": blog["id"],
                "title": blog.get("title", ""),
                "url": blog.get("url", ""),
                "chunk_text": chunk_content,
                "chunk_index": chunk_idx,
                "thumbnail_url": None
            })
    
    for video in videos:
        summary = video.get("summary", "")
        chunks = chunk_text(summary, size=_VIDEO_CHUNK_SIZE, overlap=_VIDEO_CHUNK_OVERLAP)
        
        for chunk_idx, chunk_content in enumerate(chunks):
            embedding = embed_fn(chunk_content)
            all_chunks.append(embedding)
            all_metadata.append({
                "source_type": "video",
                "source_id": video["id"],
                "video_id": video.get("video_id", ""),
                "title": video.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={video.get('video_id', '')}",
                "chunk_text": chunk_content,
                "chunk_index": chunk_idx,
                "thumbnail_url": video.get("thumbnail_url", ""),
                "channel": video.get("channel", "")
            })
    
    if not all_chunks:
        vectors = np.zeros((1, 768), dtype=np.float32)
        index = faiss.IndexFlatIP(768)
        index.add(vectors)
    else:
        vectors = np.array(all_chunks, dtype=np.float32)
        vectors = _normalize(vectors)
        
        dimension = vectors.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(vectors)
    
    faiss.write_index(index, os.path.join(_FAISS_INDEX_PATH, "index.faiss"))
    
    with open(os.path.join(_FAISS_INDEX_PATH, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, ensure_ascii=False)
    
    blogs_count = len(blogs)
    videos_count = len(videos)
    total_chunks = len(all_chunks)
    
    return {
        "blogs": blogs_count,
        "videos": videos_count,
        "total_chunks": total_chunks
    }


def load_index() -> Tuple[faiss.Index, list[dict]]:
    index_path = os.path.join(_FAISS_INDEX_PATH, "index.faiss")
    metadata_path = os.path.join(_FAISS_INDEX_PATH, "metadata.json")
    
    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        raise FileNotFoundError(
            "FAISS index not found. Run: python scripts/ingest.py"
        )
    
    index = faiss.read_index(index_path)
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    return index, metadata


def search(query_vector: list[float], k: int = _TOP_K_RESULTS) -> list[dict]:
    index, metadata = load_index()
    
    query = np.array([query_vector], dtype=np.float32)
    query = _normalize(query)
    
    k = min(k, index.ntotal)
    if k == 0:
        return []
    
    scores, indices = index.search(query, k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0 and idx < len(metadata):
            result = metadata[idx].copy()
            result["score"] = float(score)
            results.append(result)
    
    return results
