from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse
from backend.services import rag_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return await rag_service.answer_query(request.query, request.chat_history)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e) + " — Hint: run python scripts/ingest.py"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
