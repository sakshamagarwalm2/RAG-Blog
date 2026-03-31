import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Test Gemini API
print("Testing Gemini API connection...")
try:
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("FAILED: GEMINI_API_KEY not found in .env")
        exit(1)
    
    print(f"API Key: {api_key[:10]}...")
    
    genai.configure(api_key=api_key)
    
    # Test embedding
    print("\nTesting embedding model...")
    embedding_model = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
    result = genai.embed_content(
        model=embedding_model,
        content="This is a test",
        task_type="retrieval_document"
    )
    print(f"SUCCESS: Embedding works! Dimension: {len(result['embedding'])}")
    
    # Test text generation
    print("\nTesting text generation model...")
    generation_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    model = genai.GenerativeModel(generation_model)
    response = model.generate_content("Say hello in one word")
    print(f"SUCCESS: Text generation works! Response: {response.text[:50]}")
    
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()