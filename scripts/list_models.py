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
    
    # List available models
    print("\nListing available models...")
    for model in genai.list_models():
        if 'embed' in model.name.lower():
            print(f"  - {model.name}")
            print(f"    Supported methods: {model.supported_generation_methods}")
    
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()