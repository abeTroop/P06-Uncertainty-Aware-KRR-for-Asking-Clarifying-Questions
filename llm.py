from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# The default API key is read from the environment variable: GEMINI_API_KEY
# To change the API key, pass it as a parameter directly with os.getenv("YOUR_ENV_VAR)")
client = genai.Client()

def llm_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=prompt
    )
    return response.text
