import streamlit as st
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv(Path(__file__).parent.parent.parent / ".env")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Blog Manager", page_icon="📝", layout="wide")
st.title("📝 Blog Manager")
st.caption("Add and manage blog articles in MongoDB")

left, right = st.columns([4, 6])

with left:
    st.subheader("Add New Blog")
    with st.form("add_blog_form", clear_on_submit=True):
        title = st.text_input("Title *", placeholder="My awesome blog post")
        url = st.text_input("URL *", placeholder="https://yourblog.com/post-slug")
        summary = st.text_area("Summary (optional)", height=80, placeholder="One line description...")
        content = st.text_area("Content *", height=300, placeholder="Paste the full blog content here...")
        tags_input = st.text_input("Tags", placeholder="python, ai, tutorial  (comma-separated)")
        
        submitted = st.form_submit_button("➕ Add Blog", use_container_width=True)
        
        if submitted:
            if not title.strip() or not content.strip() or not url.strip():
                st.error("Title, URL, and Content are required.")
            else:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                try:
                    r = httpx.post(f"{BACKEND_URL}/blogs", json={
                        "title": title,
                        "url": url,
                        "content": content,
                        "summary": summary or None,
                        "tags": tags
                    }, timeout=30)
                    r.raise_for_status()
                    st.success(f"✓ Blog added: **{title}**")
                    st.info("Don't forget to re-index! Click 'Re-index Blogs' in the Chat page sidebar.")
                except Exception as e:
                    st.error(f"Failed to add blog: {e}")

with right:
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader("All Blogs")
    with col2:
        st.button("🔄 Refresh")
    
    try:
        r = httpx.get(f"{BACKEND_URL}/blogs", timeout=15)
        r.raise_for_status()
        blogs = r.json()
        
        st.caption(f"{len(blogs)} blogs in database")
        
        if not blogs:
            st.info("No blogs yet. Add your first blog using the form on the left.")
        
        for blog in blogs:
            created = blog.get("created_at", "")
            try:
                created_fmt = datetime.fromisoformat(created.replace("Z", "")).strftime("%d %b %Y")
            except:
                created_fmt = created[:10] if created else "Unknown"
            
            with st.expander(f"📄 {blog['title']}"):
                st.markdown(f"**URL:** [{blog['url']}]({blog['url']})")
                st.markdown(f"**Added:** {created_fmt}")
                
                if blog.get("tags"):
                    st.markdown(f"**Tags:** `{'` `'.join(blog['tags'])}`")
                
                if blog.get("summary"):
                    st.caption(blog["summary"])
                
                st.markdown("**Preview:**")
                st.text(blog["content"][:250] + "..." if len(blog["content"]) > 250 else blog["content"])
                
                if st.button(f"🗑️ Delete", key=f"del_{blog['id']}", type="secondary"):
                    try:
                        dr = httpx.delete(f"{BACKEND_URL}/blogs/{blog['id']}", timeout=15)
                        dr.raise_for_status()
                        st.success("Deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")
    
    except httpx.ConnectError:
        st.error(f"Cannot connect to backend at {BACKEND_URL}. Make sure FastAPI is running.")
    except Exception as e:
        st.error(f"Error loading blogs: {e}")
