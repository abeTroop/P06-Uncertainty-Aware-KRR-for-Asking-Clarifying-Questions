import json

from fastapi import HTTPException

from backend.llm import llm_response
from backend.prompts import master_prompt, clarification_prompt
from backend.storage import create_session, get_session, update_session


def _parse_json(text: str) -> dict:
    """Extract and parse the first JSON object found in an LLM response."""
    idx = text.find("{")
    if idx == -1:
        raise ValueError(f"No JSON object found in LLM response: {text!r}")
    return json.loads(text[idx:])


def _call_llm(prompt: str) -> dict:
    """Call the LLM and parse JSON, raising HTTP 502 on any failure."""
    try:
        raw = llm_response(prompt)
        return _parse_json(raw)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc


def process_question(question: str) -> dict:
    """
    Uncertainty estimation + decision policy in one LLM call.
    Returns session_id and either an answer or a clarifying question.
    """
    result = _call_llm(master_prompt(question))

    decision = result.get("decision", "clarify")
    if decision not in ("answer", "clarify"):
        decision = "clarify"

    uncertainty_score = result.get("uncertainty_score", 0.5)

    session_data = {
        "question": question,
        "uncertainty_score": uncertainty_score,
        "decision": decision,
        "reason": result.get("reason"),
        "direct_answer": result.get("answer"),
        "clarifying_question": result.get("clarifying_question"),
    }
    session_id = create_session(session_data)

    response = {
        "session_id": session_id,
        "decision": decision,
        "uncertainty_score": uncertainty_score,
        "reason": result.get("reason"),
    }
    if decision == "answer":
        response["answer"] = result.get("answer")
    else:
        response["clarifying_question"] = result.get("clarifying_question")

    return response


def process_clarification(session_id: str, clarification: str) -> dict:
    """
    Refine the answer after the user provides clarification.
    Updates the session log with the final answer.
    """
    session = get_session(session_id)
    if session is None:
        raise KeyError(f"Session {session_id!r} not found")

    if session.get("decision") != "clarify":
        raise KeyError(f"Session {session_id!r} was already answered directly; no clarification needed")

    result = _call_llm(clarification_prompt(
        question=session["question"],
        clarifying_question=session["clarifying_question"],
        clarification=clarification,
    ))

    update_session(session_id, {
        "clarification": clarification,
        "final_answer": result.get("final_answer"),
        "final_confidence": result.get("confidence"),
    })

    return {
        "session_id": session_id,
        "final_answer": result.get("final_answer"),
        "confidence": result.get("confidence"),
        "explanation": result.get("explanation"),
    }
