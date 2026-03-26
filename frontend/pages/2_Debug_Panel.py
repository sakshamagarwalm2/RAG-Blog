import streamlit as st
import httpx
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Debug - RAG Chat", page_icon="🔍", layout="wide")
st.title("🔍 RAG Chat Debug Panel")
st.caption("See exactly what happens when you send a message")

BACKEND_URL = "http://localhost:8000"

st.markdown("---")

st.subheader("🎬 YouTube Video Debug")

col_test1, col_test2 = st.columns([3, 1])

with col_test1:
    test_url = st.text_input("YouTube URL:", value="https://youtu.be/15OWXY88OP4", key="test_url_input")
    test_tags = st.text_input("Tags:", value="test, debug", key="test_tags_input")

with col_test2:
    st.caption(" ")
    if st.button("Test Video URL", use_container_width=True):
        from backend.services import youtube_service
        
        try:
            video_id = youtube_service.extract_video_id(test_url)
            st.info(f"Video ID: {video_id}")
            
            meta = youtube_service.get_video_metadata(test_url)
            st.success(f"Title: {meta['title']}")
            st.caption(f"Channel: {meta['channel']}")
            st.image(meta['thumbnail_url'], width=280)
            
            with st.spinner("Fetching transcript..."):
                transcript, word_count = youtube_service.fetch_transcript(video_id)
                st.success(f"Transcript fetched: {word_count} words")
                st.text_area("Preview:", transcript[:500] + "...", height=100)
        except Exception as e:
            st.error(f"Error: {str(e)[:200]}")

st.markdown("---")

with st.form("debug_form"):
    st.subheader("Send a Query")
    query = st.text_input("Question:", value="What is this blog about?")
    chat_history_enabled = st.checkbox("Include chat history (last 6 messages)", value=False)
    
    submitted = st.form_submit_button("Send & Debug", type="primary")
    
    if submitted and query:
        start_time = time.time()
        logs = []
        
        def add_log(step, data, status="info"):
            logs.append({
                "time": time.time() - start_time,
                "step": step,
                "data": data,
                "status": status
            })
        
        add_log("1. Input", {"query": query, "chat_history_enabled": chat_history_enabled})
        
        try:
            chat_history = []
            if chat_history_enabled and "messages" in st.session_state:
                chat_history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.get("messages", [])[-6:]
                ]
                add_log("2. Chat History", {"count": len(chat_history), "messages": chat_history})
            
            add_log("3. API Request", {"url": f"{BACKEND_URL}/chat", "payload": {"query": query, "chat_history": chat_history}})
            
            with st.spinner("Sending request..."):
                r = httpx.post(
                    f"{BACKEND_URL}/chat",
                    json={"query": query, "chat_history": chat_history},
                    timeout=60
                )
            
            add_log("4. API Response", {"status": r.status_code, "body": r.json() if r.status_code == 200 else r.text})
            
            if r.status_code == 200:
                data = r.json()
                add_log("5. Parsed Answer", data["answer"])
                add_log("6. Sources Found", {"count": len(data.get("sources", [])), "sources": data.get("sources", [])})
                add_log("7. Chunks Used", data.get("chunks_used", 0))
                add_log("8. Success!", {"total_time": f"{time.time() - start_time:.2f}s"}, status="success")
            else:
                add_log("Error", {"message": r.text}, status="error")
                
        except Exception as e:
            add_log("Exception", {"error": str(e)}, status="error")
        
        st.session_state.debug_logs = logs
        
        with st.expander("📊 View Raw Log Data (JSON)"):
            st.json(logs)

if "debug_logs" in st.session_state:
    st.markdown("---")
    st.subheader("Execution Log")
    
    for i, log in enumerate(st.session_state.debug_logs):
        col1, col2 = st.columns([1, 5])
        
        with col1:
            if log["status"] == "success":
                st.success(f"{log['time']:.3f}s")
            elif log["status"] == "error":
                st.error(f"{log['time']:.3f}s")
            else:
                st.info(f"{log['time']:.3f}s")
        
        with col2:
            st.markdown(f"**{log['step']}**")
            
            if log["step"] in ["1. Input", "3. API Request", "6. Sources Found", "2. Chat History", "7. Chunks Used"]:
                st.json(log["data"])
            elif log["step"] in ["5. Parsed Answer"]:
                st.text_area("Answer:", log["data"], height=100, key=f"answer_{i}", disabled=True)
            else:
                st.write(log["data"])

st.markdown("---")

st.subheader("📁 System Status")

col1, col2, col3 = st.columns(3)

with col1:
    try:
        r = httpx.get(f"{BACKEND_URL}/health", timeout=5)
        if r.status_code == 200:
            st.success("Backend: Running")
        else:
            st.error(f"Backend: Error {r.status_code}")
    except:
        st.error("Backend: Not Connected")

with col2:
    try:
        r = httpx.get(f"{BACKEND_URL}/blogs", timeout=5)
        if r.status_code == 200:
            blogs = r.json()
            st.info(f"MongoDB: {len(blogs)} blogs")
        else:
            st.warning(f"MongoDB: Error {r.status_code}")
    except Exception as e:
        st.warning(f"MongoDB: Not Connected")

with col3:
    import os
    index_path = os.path.join(os.path.dirname(__file__).replace("\\frontend\\pages", ""), "faiss_index", "index.faiss")
    if os.path.exists(index_path):
        size = os.path.getsize(index_path)
        st.info(f"FAISS Index: {size} bytes")
    else:
        st.warning("FAISS Index: Not Found")

st.markdown("---")

with st.expander("ℹ️ How RAG Works"):
    st.markdown("""
    **Retrieval-Augmented Generation (RAG) Flow:**
    
    1. **User Query** - You ask a question
    2. **Embedding** - The query is converted to a vector using Gemini embeddings
    3. **Vector Search** - FAISS searches for similar text chunks in the index
    4. **Context Assembly** - Relevant chunks are combined as context
    5. **LLM Generation** - Gemini generates an answer based on the context
    6. **Response** - The answer and source URLs are returned
    """)
