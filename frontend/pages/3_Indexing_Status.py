import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(layout="wide")

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000") # NestJS backend

st.title("Indexing Status")

@st.cache_data(ttl=5)
def get_indexing_status():
    try:
        response = requests.get(f"{FASTAPI_URL}/indexing/status/blogs")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to backend at {FASTAPI_URL}. Please ensure the backend is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching indexing status: {e}")
        return None

def trigger_reindex(force: bool = False):
    try:
        with st.spinner(f"Triggering re-index (force={force})... This may take a while."):
            response = requests.post(f"{FASTAPI_URL}/indexing/reindex", params={"force": str(force).lower()})
            response.raise_for_status()
            st.success("Re-indexing process initiated successfully!")
            st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Error triggering re-index: {e}")

status_data = get_indexing_status()

if status_data:
    st.subheader("Indexed Blogs")
    if status_data['indexed']:
        indexed_df = pd.DataFrame(status_data['indexed'])
        st.dataframe(indexed_df[['title', 'url', 'updated_at']], use_container_width=True)
    else:
        st.info("No blogs currently indexed.")

    st.subheader("Unindexed Blogs")
    if status_data['unindexed']:
        unindexed_df = pd.DataFrame(status_data['unindexed'])
        st.dataframe(unindexed_df[['title', 'url', 'updated_at']], use_container_width=True)
    else:
        st.success("All blogs are indexed!")

    st.subheader("Re-index Options")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Trigger Full Re-index (Updates existing & adds new)"):
            trigger_reindex()
    with col2:
        if st.button("Force Re-index All (Clears and rebuilds index)"):
            trigger_reindex(force=True)

    st.markdown("---")
    st.markdown("Please note that indexing is an asynchronous process. It may take some time for changes to reflect.")
else:
    st.warning("Indexing status could not be loaded. Please check the backend server.")

