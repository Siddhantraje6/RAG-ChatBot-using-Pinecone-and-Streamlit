from google import genai

from config import config

genai_client = None

async def init_genai():
    """Initialize the google genai client"""
    global genai_client

    try:
        genai_client = genai.Client(api_key = config.GEMINI_API_KEY)
    except Exception as e:
        raise RuntimeError(f"Failed to connect with google-genai: {e}")

def get_genai_client():
    """Return genai client"""
    if genai_client is None:
        raise RuntimeError("google genai client not connected")
    return genai_client
