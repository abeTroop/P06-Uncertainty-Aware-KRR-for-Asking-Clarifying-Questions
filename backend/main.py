from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm import llm_response
from orchestrator import process_question, process_clarification
from storage import get_logs

app = FastAPI(
    title="Uncertainty-Aware QA Backend",
    description="Asks clarifying questions when uncertain; answers directly when confident.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

class QuestionRequest(BaseModel):
    question: str

class ClarifyRequest(BaseModel):
    session_id: str
    clarification: str


# ---------- Endpoints ----------

@app.post("/llm")
def raw_llm(payload: Prompt):
    """Pass a raw prompt directly to the LLM (kept for compatibility)."""
    return {"response": llm_response(payload.prompt)}


@app.post("/ask")
def ask(payload: QuestionRequest):
    """
    Submit a user question.
    Returns either a direct answer (low uncertainty) or a clarifying question (high uncertainty).
    Always includes session_id for follow-up calls to /clarify.
    """
    return process_question(payload.question)


@app.post("/clarify")
def clarify(payload: ClarifyRequest):
    """
    Submit the user's clarification for a previous /ask session.
    Returns the refined final answer.
    """
    try:
        return process_clarification(payload.session_id, payload.clarification)
    except KeyError as e:
        msg = str(e)
        status = 400 if "already answered" in msg else 404
        raise HTTPException(status_code=status, detail=msg)


@app.get("/logs")
def logs():
    """Retrieve all interaction logs for evaluation and analysis."""
    return {"logs": get_logs()}
