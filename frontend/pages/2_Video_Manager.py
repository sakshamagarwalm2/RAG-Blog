import streamlit as st
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv(Path(__file__).parent.parent.parent / ".env")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Video Manager", page_icon="🎬", layout="wide")
st.title("🎬 Video Manager")
st.caption("Add YouTube videos — transcripts are fetched automatically and indexed for chat")

left, right = st.columns([4, 6])

with left:
    st.subheader("Add YouTube Video")
    
    st.info(
        "**How it works:**\n"
        "1. Paste a YouTube URL\n"
        "2. Transcript is fetched automatically (no API key needed)\n"
        "3. If transcript is long, Gemini creates a detailed summary\n"
        "4. Video is saved and ready to index\n\n"
        "⚠️ Video must have captions/subtitles enabled on YouTube."
    )
    
    add_mode = st.radio("Add Mode:", ["Auto-fetch transcript", "Manual transcript"], horizontal=True)
    
    with st.form("add_video_form", clear_on_submit=True):
        
        if add_mode == "Auto-fetch transcript":
            youtube_url = st.text_input(
                "YouTube URL *",
                placeholder="https://www.youtube.com/watch?v=..."
            )
            tags_input = st.text_input(
                "Tags (optional)",
                placeholder="python, machine learning, tutorial"
            )
            transcript_text = ""
        else:
            st.warning("Use this if YouTube doesn't have captions - paste your own transcript")
            youtube_url = st.text_input(
                "YouTube URL *",
                placeholder="https://www.youtube.com/watch?v=..."
            )
            transcript_text = st.text_area(
                "Paste Transcript Here *",
                height=200,
                placeholder="Paste the video transcript text here..."
            )
            tags_input = st.text_input(
                "Tags (optional)",
                placeholder="python, machine learning, tutorial"
            )
        
        submitted = st.form_submit_button("➕ Add Video", use_container_width=True)
        
        if submitted:
            if not youtube_url.strip():
                st.error("YouTube URL is required.")
            elif add_mode == "Manual transcript" and not transcript_text.strip():
                st.error("Transcript text is required for manual mode.")
            else:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                
                if add_mode == "Auto-fetch transcript":
                    with st.spinner("Fetching transcript and processing..."):
                        try:
                            r = httpx.post(
                                f"{BACKEND_URL}/videos",
                                json={"youtube_url": youtube_url.strip(), "tags": tags},
                                timeout=120
                            )
                            
                            if r.status_code == 409:
                                st.warning("This video has already been added.")
                            elif r.status_code == 400:
                                st.error(r.json().get("detail", "Invalid URL or no transcript available."))
                            else:
                                r.raise_for_status()
                                data = r.json()
                                st.success(f"✓ Added: **{data['title']}**")
                                
                                if data.get("was_summarized"):
                                    st.info(f"Transcript was {data['transcript_word_count']:,} words — Gemini created a detailed summary.")
                                else:
                                    st.info(f"Transcript was {data['transcript_word_count']:,} words — stored as-is (short enough).")
                                
                                st.warning("⚠️ Remember to Re-index!")
                        except httpx.ConnectError:
                            st.error(f"Cannot connect to backend at {BACKEND_URL}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    # Manual transcript mode - send to custom endpoint
                    with st.spinner("Processing manual transcript..."):
                        try:
                            r = httpx.post(
                                f"{BACKEND_URL}/videos/manual",
                                json={
                                    "youtube_url": youtube_url.strip(), 
                                    "transcript_raw": transcript_text.strip(),
                                    "tags": tags
                                },
                                timeout=60
                            )
                            
                            if r.status_code == 409:
                                st.warning("This video has already been added.")
                            else:
                                r.raise_for_status()
                                data = r.json()
                                st.success(f"✓ Added: **{data['title']}**")
                                st.info(f"Transcript: {data['transcript_word_count']:,} words")
                                st.warning("⚠️ Remember to Re-index!")
                        except httpx.ConnectError:
                            st.error(f"Cannot connect to backend at {BACKEND_URL}")
                        except Exception as e:
                            st.error(f"Error: {e}")

with right:
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader("All Videos")
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    try:
        r = httpx.get(f"{BACKEND_URL}/videos", timeout=15)
        r.raise_for_status()
        videos = r.json()
        
        st.caption(f"{len(videos)} videos in database")
        
        if not videos:
            st.info("No videos yet. Add your first video using the form on the left.")
        
        for video in videos:
            created = video.get("created_at", "")
            try:
                created_fmt = datetime.fromisoformat(created.replace("Z", "")).strftime("%d %b %Y")
            except:
                created_fmt = created[:10] if created else "Unknown"
            
            with st.expander(f"🎬 {video['title']}"):
                thumb_col, info_col = st.columns([2, 3])
                
                with thumb_col:
                    if video.get("thumbnail_url"):
                        st.image(video["thumbnail_url"], use_column_width=True)
                
                with info_col:
                    st.markdown(f"**Channel:** {video.get('channel', 'Unknown')}")
                    st.markdown(f"**Added:** {created_fmt}")
                    st.markdown(f"**Transcript:** {video.get('transcript_word_count', 0):,} words")
                    
                    if video.get("was_summarized"):
                        st.success("✓ AI summary created")
                    else:
                        st.info("Stored as-is (short transcript)")
                    
                    if video.get("tags"):
                        st.markdown(f"**Tags:** `{'` `'.join(video['tags'])}`")
                    
                    yt_url = video.get("youtube_url", "")
                    st.markdown(f"[▶ Watch on YouTube]({yt_url})")
                
                if st.button(f"🗑️ Delete", key=f"del_video_{video['id']}", type="secondary"):
                    try:
                        dr = httpx.delete(f"{BACKEND_URL}/videos/{video['id']}", timeout=15)
                        dr.raise_for_status()
                        st.success("Deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")
    
    except httpx.ConnectError:
        st.error(f"Cannot connect to backend at {BACKEND_URL}")
    except Exception as e:
        st.error(f"Error loading videos: {e}")