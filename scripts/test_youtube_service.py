import sys
from pathlib import Path

if sys.prefix == sys.base_prefix:
    print("ERROR: Virtual environment is not activated.")
    print("Run: source venv/bin/activate  (macOS/Linux)")
    print("Run: venv\\Scripts\\activate.bat  (Windows)")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services import youtube_service, mongo_service

print("=" * 60)
print("YouTube Service Test Script")
print("=" * 60)

TEST_URL = "https://youtu.be/15OWXY88OP4"

print(f"\n1. Testing extract_video_id...")
try:
    video_id = youtube_service.extract_video_id(TEST_URL)
    print(f"   [OK] Video ID extracted: {video_id}")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")

print(f"\n2. Testing get_video_metadata...")
try:
    metadata = youtube_service.get_video_metadata(video_id)
    print(f"   [OK] Title: {metadata['title']}")
    print(f"   [OK] Channel: {metadata['channel']}")
    print(f"   [OK] Thumbnail: {metadata['thumbnail_url']}")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")

print(f"\n3. Testing fetch_transcript...")
try:
    transcript, word_count = youtube_service.fetch_transcript(video_id)
    print(f"   [OK] Transcript fetched!")
    print(f"   [OK] Word count: {word_count}")
    print(f"   [OK] First 200 chars: {transcript[:200]}...")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")
    print(f"   -> This video likely has no captions available")

print(f"\n4. Testing process_youtube_url (full pipeline)...")
try:
    result = youtube_service.process_youtube_url(TEST_URL, ["test", "demo"])
    print(f"   [OK] Video processed successfully!")
    print(f"   [OK] Video ID: {result['video_id']}")
    print(f"   [OK] Title: {result['title']}")
    print(f"   [OK] Channel: {result['channel']}")
    print(f"   [OK] Word count: {result['transcript_word_count']}")
    print(f"   [OK] Was summarized: {result['was_summarized']}")
    print(f"   [OK] Summary length: {len(result['summary'])} chars")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")

print(f"\n5. Testing MongoDB operations...")
try:
    print(f"   [OK] Videos count before: {mongo_service.get_videos_count()}")
    
    result = youtube_service.process_youtube_url(TEST_URL, ["test", "demo"])
    saved = mongo_service.create_video(result)
    print(f"   [OK] Video saved to MongoDB with ID: {saved['id']}")
    
    print(f"   [OK] Videos count after: {mongo_service.get_videos_count()}")
    
    videos = mongo_service.get_all_videos()
    print(f"   [OK] Retrieved {len(videos)} videos from MongoDB")
    
    if mongo_service.video_exists(result['video_id']):
        print(f"   [OK] video_exists() returns True")
    
    deleted = mongo_service.delete_video(saved['id'])
    print(f"   [OK] Deleted video: {deleted}")
    
    print(f"   [OK] Final videos count: {mongo_service.get_videos_count()}")
    
except Exception as e:
    print(f"   [FAIL] Failed: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)