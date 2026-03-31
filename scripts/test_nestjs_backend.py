import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    resp = requests.get(f"{BASE_URL}/health")
    print(resp.json())
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_blogs():
    print("\nTesting /blogs...")
    # Add a blog
    payload = {
        "title": "Test Blog",
        "content": "This is a test blog content for RAG testing. It should be long enough to be chunked if needed.",
        "url": "http://test.com/blog",
        "tags": ["test"]
    }
    resp = requests.post(f"{BASE_URL}/blogs", json=payload)
    print("Add blog:", resp.json())
    assert resp.status_code == 201
    blog_id = resp.json()["id"]

    # Get blogs
    resp = requests.get(f"{BASE_URL}/blogs")
    print("Get blogs count:", len(resp.json()))
    assert resp.status_code == 200

    # Delete blog
    resp = requests.delete(f"{BASE_URL}/blogs/{blog_id}")
    print("Delete blog:", resp.json())
    assert resp.status_code == 200

def test_videos():
    print("\nTesting /videos...")
    # Add a video (use a short video with transcript)
    payload = {
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", # Rick Astley - Never Gonna Give You Up
        "tags": ["music"]
    }
    resp = requests.post(f"{BASE_URL}/videos", json=payload)
    print("Add video:", resp.json())
    if resp.status_code == 409:
        print("Video already exists, continuing...")
    else:
        assert resp.status_code == 201
    
    # Get videos
    resp = requests.get(f"{BASE_URL}/videos")
    print("Get videos count:", len(resp.json()))
    assert resp.status_code == 200

def test_ingest():
    print("\nTesting /ingest/rebuild...")
    resp = requests.post(f"{BASE_URL}/ingest/rebuild")
    print("Rebuild index:", resp.json())
    assert resp.status_code == 201

def test_chat():
    print("\nTesting /chat...")
    payload = {
        "query": "What is the test blog about?",
        "chat_history": []
    }
    resp = requests.post(f"{BASE_URL}/chat", json=payload)
    print("Chat response:", resp.json()["answer"])
    assert resp.status_code == 201

if __name__ == "__main__":
    try:
        test_health()
        test_blogs()
        # test_videos() # Might fail if transcript is disabled or ytdl-core issues
        test_ingest()
        test_chat()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
