import google.generativeai as genai
import os

# Use either GOOGLE_API_KEY or GEMINI_API_KEY
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def get_embedding(text: str):
    if not API_KEY:
        return None
    try:
        # models/embedding-001 has 768 dimensions
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
