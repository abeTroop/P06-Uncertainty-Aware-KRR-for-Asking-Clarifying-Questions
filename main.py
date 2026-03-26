from fastapi import FastAPI
from pydantic import BaseModel
from llm import llm_response

app = FastAPI()

class Prompt(BaseModel):
    prompt: str

@app.put("/llm")
def llm(prompt: Prompt):
    return {"response": llm_response(prompt.prompt)}
