from fastapi import FastAPI
from pydantic import BaseModel
from backend.llm import llm_response

app = FastAPI()

class Prompt(BaseModel):
    prompt: str

@app.put("/llm")
def llm(prompt: Prompt):
    return {"response": llm_response(prompt.prompt)}
