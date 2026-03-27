
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from api/.env
load_dotenv("api/.env")

def test_openai_connection():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in api/.env")
        return

    try:
        client = OpenAI(api_key=api_key)
        # Simple call to verify auth
        response = client.models.list()
        
        # specific check (optional, just presence of list proves auth)
        gpt4_exists = any("gpt-4" in m.id for m in response.data)
        
        print("✅ OpenAI API connection successful!")
        print(f"   Found {len(response.data)} models.")
        if gpt4_exists:
            print("   GPT-4 access confirmed.")
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")

if __name__ == "__main__":
    test_openai_connection()
