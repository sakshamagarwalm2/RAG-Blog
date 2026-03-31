import os
import re
import time
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import google.generativeai as genai
import yt_dlp

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_WORDS = int(os.getenv("VIDEO_SUMMARY_MAX_WORDS", 3000))


def extract_video_id(url: str) -> str:
    pattern = r'(?:v=|youtu\.be/|embed/|shorts/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid YouTube URL — could not extract video ID")
    return match.group(1)


def get_video_metadata(video_id: str) -> dict:
    try:
        from pytube import YouTube
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        return {
            "title": yt.title or f"YouTube Video ({video_id})",
            "channel": yt.author or "Unknown",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        }
    except Exception:
        return {
            "title": f"YouTube Video ({video_id})",
            "channel": "Unknown",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        }


def fetch_transcript(video_id: str) -> tuple[str, int]:
    text = ""
    
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
        text = " ".join([entry["text"] for entry in transcript])
    except Exception:
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB']).fetch()
            text = " ".join([entry["text"] for entry in transcript])
        except Exception:
            try:
                ydl_opts = {
                    'writesubtitles': True,
                    'skipdownload': True,
                    'subtitlesformats': ['srt', 'vtt', 'json3'],
                    'subtitle': ['en', 'en-US', 'en-GB'],
                    'quiet': True,
                    'no_warn': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                    subtitles = info.get('subtitles', {})
                    if subtitles:
                        sub_lang = 'en' if 'en' in subtitles else list(subtitles.keys())[0]
                        sub_data = subtitles[sub_lang][0]
                        if 'data' in sub_data:
                            text = sub_data['data']
            except Exception as e:
                raise ValueError(f"This video has no available transcript. Only videos with captions/subtitles can be added. Error: {str(e)}")
    
    if not text or len(text) < 10:
        raise ValueError("This video has no available transcript. Only videos with captions/subtitles can be added.")
    
    text = re.sub(r'\[Music\]', '', text)
    text = re.sub(r'\[Applause\]', '', text)
    text = re.sub(r'\[Laughter\]', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    word_count = len(text.split())
    return text, word_count


def summarize_transcript(transcript: str, title: str) -> str:
    prompt = f"""You are an expert content summarizer. Your task is to create a comprehensive, detailed summary of a YouTube video transcript.

Video Title: {title}

Full Transcript:
{transcript}

Create a detailed summary that includes:
1. **Main Topic**: What is this video fundamentally about?
2. **Key Points**: List all major points covered (be thorough, include 8-15 bullet points)
3. **Important Details**: Specific facts, statistics, examples, code snippets, or techniques mentioned
4. **Concepts Explained**: Any technical concepts, terms, or frameworks introduced
5. **Practical Takeaways**: What can a viewer actually do or apply after watching this?
6. **Conclusions**: What conclusions or recommendations does the video make?

Write the summary in flowing paragraphs under each heading. Be detailed enough that someone who hasn't watched the video would fully understand all the content. Preserve technical accuracy — do not simplify or omit technical details.
"""
    
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                raise e
    
    return transcript


def process_youtube_url(url: str, tags: list[str] = []) -> dict:
    video_id = extract_video_id(url)
    
    metadata = get_video_metadata(video_id)
    
    transcript_text, word_count = fetch_transcript(video_id)
    
    if word_count > MAX_WORDS:
        summary = summarize_transcript(transcript_text, metadata["title"])
        was_summarized = True
    else:
        summary = transcript_text
        was_summarized = False
    
    return {
        "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
        "video_id": video_id,
        "title": metadata["title"],
        "channel": metadata["channel"],
        "thumbnail_url": metadata["thumbnail_url"],
        "transcript_raw": transcript_text,
        "transcript_word_count": word_count,
        "summary": summary,
        "was_summarized": was_summarized,
        "tags": tags,
    }