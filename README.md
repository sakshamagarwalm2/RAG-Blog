# RAG Blog Chat

A RAG (Retrieval-Augmented Generation) chat application with MongoDB Atlas, FAISS vector store, and Google Gemini API.

## Features

- **Chat with your blogs** — Ask questions and get answers based on your blog content
- **Blog Manager UI** — Add, view, and delete blogs from MongoDB
- **FAISS Vector Search** — Fast similarity search over blog chunks
- **Gemini AI** — Uses Google Gemini for embeddings and LLM responses

## Prerequisites

```bash
python3 --version   # need 3.10+
pip3 --version
```

## Quick Start (Recommended)

### Use PowerShell Scripts

```powershell
# Navigate to scripts folder
cd scripts

# Run the main menu script
.\run.ps1
```

Options:
- **[1] Setup** - Create venv & install dependencies
- **[2] Test connections** - Verify MongoDB & Gemini
- **[3] Build index** - Create FAISS index
- **[6] Run all** - Start both servers together

### Manual Setup (Alternative)

#### 1. Create virtual environment

```bash
# Create venv
python3 -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Activate on Windows (Command Prompt):
venv\Scripts\activate.bat

# Activate on Windows (PowerShell):
venv\Scripts\Activate.ps1
```

#### 2. Install dependencies

```bash
# venv must be activated
pip install -r requirements.txt
```

#### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Key | Where to get it |
|-----|-----------------|
| `MONGO_URI` | MongoDB Atlas → Connect → Drivers → copy connection string |
| `MONGO_DB_NAME` | Database name (e.g., `blog_db`) |
| `MONGO_COLLECTION_NAME` | Collection name (e.g., `blogs`) |
| `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |

#### 4. Test connections

```bash
python scripts/test_connection.py
```

#### 5. Build FAISS index

```bash
python scripts/ingest.py
```

#### 6. Start servers

**Option A - Run both servers:**
```bash
python scripts/run.py
# Select option 6
```

**Option B - Manual start:**
```bash
# Terminal 1 - Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 - Frontend
streamlit run frontend/app.py --server.port 8501
```

## Usage

### Adding Blogs

1. Go to the Blog Manager page (in Streamlit sidebar)
2. Fill in title, URL, content, and optional tags
3. Click "Add Blog"
4. **Important:** Re-index by clicking "Re-index Blogs" in the sidebar

### Chatting

1. Ask questions about your blogs
2. View sources by expanding the "Sources" section
3. Chat history is maintained within the session

## Project Structure

```
rag-blog-chat/
├── .env                    # Secrets (create from .env.example)
├── requirements.txt        # Python dependencies
├── README.md
│
├── backend/
│   ├── main.py            # FastAPI entry point
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── mongo_service.py
│   │   ├── embeddings_service.py
│   │   ├── faiss_service.py
│   │   └── rag_service.py
│   └── routes/            # API endpoints
│
├── frontend/
│   ├── app.py             # Chat UI
│   └── pages/
│       └── 1_Blog_Manager.py
│
└── scripts/
    ├── run.py             # Interactive menu (Python)
    ├── run.ps1            # Interactive menu (PowerShell)
    ├── launch.ps1         # Quick launcher
    ├── test_connection.py  # Test MongoDB & Gemini
    └── ingest.py           # Build FAISS index
```

## Troubleshooting

### MongoDB connection failed
- Verify `MONGO_URI` in `.env` is correct
- Check MongoDB Atlas IP whitelist allows your IP

### Gemini API failed
- Verify `GEMINI_API_KEY` in `.env`
- Check API key has proper permissions

### FAISS index not found
- Run `python scripts/ingest.py`
- Or click "Re-index Blogs" in the Streamlit sidebar

### Port already in use
- Change port in command: `--port 8502`
- Update `BACKEND_URL` in `.env` if backend port changes
