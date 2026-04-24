import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

def llm_response(prompt: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
