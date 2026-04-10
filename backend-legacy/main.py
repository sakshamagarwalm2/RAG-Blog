from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat_router, blogs_router, ingest_router
from routes.videos import router as videos_router

app = FastAPI(title="RAG Blog Chat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat_router)
app.include_router(blogs_router)
app.include_router(ingest_router)
app.include_router(videos_router)


@app.get("/health")
def health():
    return {"status": "ok", "message": "RAG Blog Chat API is running"}


@app.on_event("startup")
def startup():
    print("RAG Blog Chat API started")
    print("Docs: http://localhost:8000/docs")
