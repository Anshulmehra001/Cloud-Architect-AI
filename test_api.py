"""
Quick test script to verify Gemini API is working
Run with: python test_api.py
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()

# Configure API
api_key = os.environ.get('GEMINI_API_KEY')
model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')

print("=" * 50)
print("GEMINI API TEST")
print("=" * 50)
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print(f"Model: {model_name}")
print()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    print("Sending test request...")
    response = model.generate_content("Say 'Hello, Cloud Architect AI is working!' in one sentence.")
    
    print("\n✓ SUCCESS!")
    print(f"Response: {response.text}")
    print("\nYour API is working correctly!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check your API key is valid")
    print("2. Ensure billing is enabled")
    print("3. Wait 60 seconds if you see rate limit errors")
    print("=" * 50)
