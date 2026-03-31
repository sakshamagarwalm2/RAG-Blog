# RAG Blog Chat

A RAG (Retrieval-Augmented Generation) chat application with MongoDB Atlas, FAISS vector store, and Google Gemini API.

## Features

- **Chat with your blogs** — Ask questions and get answers based on your blog content
- **Blog Manager UI** — Add, view, and delete blogs from MongoDB
- **FAISS Vector Search** — Fast similarity search over blog chunks
- **Gemini AI** — Uses Google Gemini for embeddings and LLM responses

## Prerequisites

### Python (for Streamlit Frontend and Embedding Generation)

Ensure Python 3.10+ is installed. On Windows, make sure to add Python to your system's PATH during installation.

To check your Python version:
```bash
python --version
```
If `python` command doesn't work, try `python3 --version`.

### Node.js and npm (for NestJS Backend)

Ensure Node.js (which includes npm) is installed.
```bash
node --version
npm --version
```

## Quick Start (Recommended)

### Manual Setup

#### 1. Configure Environment

Copy the example environment file and fill in your credentials:
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

#### 2. Setup Python Virtual Environment and Dependencies

```bash
# Create venv
python -m venv venv

# Activate on Windows (Command Prompt):
venv\Scripts\activate.bat
# Activate on Windows (PowerShell):
venv\Scripts\Activate.ps1
# Activate on macOS/Linux:
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

#### 3. Setup NestJS Backend and Dependencies

```bash
cd backend
npm install
cd ..
```

#### 4. Build FAISS index

```bash
python scripts/ingest.py
```

#### 5. Start Servers

**In one terminal, start the NestJS Backend:**
```bash
cd backend
npm run start:dev
```
The NestJS backend will typically run on `http://localhost:3000`.

**In a separate terminal, start the Streamlit Frontend:**
```bash
# Make sure you are in the project root directory (e.g., D:\Recks\RAG-Blog)
# Activate venv if you haven't already in this terminal (e.g., venv\Scripts\Activate.ps1)
streamlit run frontend/app.py --server.port 8501
```
The Streamlit frontend will typically run on `http://localhost:8501`.

## NestJS Backend API Endpoints

The NestJS backend provides the following API endpoints:

### `blogs`
-   **GET /blogs**: Get all blogs.
-   **POST /blogs**: Add a new blog.
    *   Body: `{ "title": "string", "content": "string", "url": "string", "tags"?: string[] }`
-   **DELETE /blogs/:id**: Delete a blog.

### `chat`
-   **POST /chat**: Send a chat message and get a RAG-based response.
    *   Body: `{ "query": "string", "chat_history"?: [{ "role": "string", "content": "string" }] }`

### `ingest`
-   **POST /ingest/rebuild**: Rebuild the vector index from all blogs and videos.

### `videos`
-   **GET /videos**: Get all videos.
-   **POST /videos**: Add a new video by URL.
    *   Body: `{ "youtube_url": "string", "tags"?: string[] }`
-   **POST /videos/manual**: Add a video with manual transcript.
    *   Body: `{ "youtube_url": "string", "transcript_raw": "string", "tags"?: string[] }`
-   **DELETE /videos/:id**: Delete a video.

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
├── requirements.txt        # Python dependencies for frontend and Python services
├── README.md
│
├── backend/                # NestJS Backend
│   ├── package.json        # Node.js dependencies and scripts
│   ├── src/                # NestJS source code
│   │   ├── main.ts         # Entry point
│   │   ├── app.module.ts
│   │   ├── blogs/          # Blog related modules
│   │   ├── chat/           # Chat related modules
│   │   ├── ingest/         # Ingest related modules
│   │   └── videos/         # Video related modules
│   └── tsconfig.json       # TypeScript configuration
│
├── frontend/               # Streamlit Frontend
│   ├── app.py              # Chat UI
│   └── pages/
│       └── 1_Blog_Manager.py
│
└── scripts/                # Utility scripts
    ├── run.ps1             # PowerShell interactive menu
    ├── test_connection.py  # Test MongoDB & Gemini connection
    └── ingest.py           # Build FAISS index
```

## Troubleshooting

### Python was not found
- Ensure Python 3.10+ is installed and added to your system PATH.
- On Windows, try using `python` instead of `python3` in commands.

### MongoDB connection failed
- Verify `MONGO_URI` in `.env` is correct.
- Check MongoDB Atlas IP whitelist allows your IP.

### Gemini API failed
- Verify `GEMINI_API_KEY` in `.env`.
- Check API key has proper permissions.

### FAISS index not found
- Run `python scripts/ingest.py`.
- Or click "Re-index Blogs" in the Streamlit sidebar.

### Port already in use
- For NestJS, you might need to adjust the port in `main.ts` or through environment variables if applicable.
- For Streamlit, change port in command: `--server.port 8502`.
- Update `BACKEND_URL` in `.env` if backend port changes.
