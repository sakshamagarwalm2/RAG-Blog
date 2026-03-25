import os
import google.generativeai as genai
from dotenv import load_dotenv
from backend.models.schemas import ChatResponse
from backend.services import embeddings_service, faiss_service

load_dotenv()

_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

PROMPT_TEMPLATE = """You are a helpful assistant that answers questions based on blog articles.

Use ONLY the information provided in the context below to answer the question.
If the answer is not in the context, say exactly: "I don't have enough information in the available blogs to answer this."
Do NOT make up information. Do NOT use external knowledge.

Context from relevant blog articles:
---
{context}
---

Previous conversation:
{chat_history_text}

User question: {query}

Answer in a clear, helpful way. Do not list sources in your answer — they will be shown separately.
"""


async def answer_query(query: str, chat_history: list[dict]) -> ChatResponse:
    query_embedding = embeddings_service.embed_query(query)
    
    results = faiss_service.search(query_embedding, k=_TOP_K_RESULTS)
    
    unique_sources = {}
    for r in results:
        url = r["url"]
        if url not in unique_sources:
            unique_sources[url] = {
                "title": r["title"],
                "url": url
            }
    sources = list(unique_sources.values())
    
    context = "\n---\n".join(r["chunk_text"] for r in results)
    
    chat_history_text = ""
    for msg in chat_history:
        role = "Human" if msg.get("role") == "user" else "Assistant"
        chat_history_text += f"{role}: {msg.get('content', '')}\n"
    
    prompt = PROMPT_TEMPLATE.format(
        context=context or "No relevant context found.",
        chat_history_text=chat_history_text or "No previous conversation.",
        query=query
    )
    
    model = genai.GenerativeModel(_GEMINI_MODEL)
    response = model.generate_content(prompt)
    answer = response.text
    
    return ChatResponse(
        answer=answer,
        sources=sources,
        chunks_used=len(results)
    )
