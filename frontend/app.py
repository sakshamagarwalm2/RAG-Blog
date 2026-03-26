import streamlit as st
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Blog Chat", page_icon="💬", layout="centered")
st.title("💬 Blog Assistant")
st.caption(f"Ask me anything about our blog articles and videos · Backend: {BACKEND_URL}")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("⚙️ Re-index Blogs & Videos", use_container_width=True):
        with st.spinner("Re-indexing..."):
            try:
                r = httpx.post(f"{BACKEND_URL}/ingest", timeout=120)
                data = r.json()
                st.success(f"Indexed {data['blogs_indexed']} blogs, {data['chunks_created']} chunks")
            except Exception as e:
                st.error(f"Failed: {e}")
    
    st.divider()
    st.caption("After adding new blogs or videos, click Re-index or run:\n`python scripts/ingest.py`")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander(f"📚 Sources ({len(msg['sources'])})"):
                for s in msg["sources"]:
                    if s.get("source_type") == "video":
                        video_id = s.get("video_id")
                        st.markdown(f"**🎬 {s['title']}**")
                        if s.get("channel"):
                            st.caption(f"Channel: {s['channel']}")
                        
                        if video_id:
                            st.markdown(f"""
                            <iframe
                                width="100%"
                                height="200"
                                src="https://www.youtube.com/embed/{video_id}"
                                frameborder="0"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowfullscreen
                                style="border-radius: 8px;">
                            </iframe>
                            """, unsafe_allow_html=True)
                        st.markdown(f"[▶ Open on YouTube]({s['url']})")
                        st.divider()
                    else:
                        st.markdown(f"- 📄 [{s['title']}]({s['url']})")

if prompt := st.chat_input("Ask about our blogs..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching blogs and videos and generating answer..."):
            try:
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[-6:]
                ]
                r = httpx.post(
                    f"{BACKEND_URL}/chat",
                    json={"query": prompt, "chat_history": history},
                    timeout=60
                )
                r.raise_for_status()
                data = r.json()
                answer = data["answer"]
                sources = data.get("sources", [])
                
                st.write(answer)
                if sources:
                    with st.expander(f"📚 Sources ({len(sources)})"):
                        for s in sources:
                            if s.get("source_type") == "video":
                                video_id = s.get("video_id")
                                st.markdown(f"**🎬 {s['title']}**")
                                if s.get("channel"):
                                    st.caption(f"Channel: {s['channel']}")
                                
                                if video_id:
                                    st.markdown(f"""
                                    <iframe
                                        width="100%"
                                        height="200"
                                        src="https://www.youtube.com/embed/{video_id}"
                                        frameborder="0"
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                        allowfullscreen
                                        style="border-radius: 8px;">
                                    </iframe>
                                    """, unsafe_allow_html=True)
                                st.markdown(f"[▶ Open on YouTube]({s['url']})")
                                st.divider()
                            else:
                                st.markdown(f"- 📄 [{s['title']}]({s['url']})")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            
            except httpx.ConnectError:
                st.error(f"Cannot connect to backend at {BACKEND_URL}. Make sure FastAPI is running.")
            except Exception as e:
                st.error(f"Error: {e}")
