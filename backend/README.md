# P06 — Uncertainty-Aware KRR for Asking Clarifying Questions

A backend system that estimates uncertainty in user questions and decides whether to answer directly or ask a targeted clarifying question before responding.

## How It Works

1. User submits a question to `/ask`
2. The system prompts an LLM to self-assess uncertainty on a 0–1 scale
3. If uncertainty ≤ 0.4 → answer directly
4. If uncertainty > 0.4 → return a clarifying question
5. User submits their clarification to `/clarify`
6. The system refines and returns a more accurate final answer
7. All interactions are logged and retrievable via `/logs`

## Project Structure

```
.
├── main.py          # FastAPI app and route definitions
├── orchestrator.py  # Core logic: uncertainty assessment, session flow
├── prompts.py       # LLM prompt templates
├── llm.py           # Gemini API client wrapper
├── storage.py       # In-memory session and log store
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with your Gemini API key:

```
GEMINI_API_KEY=your_key_here
```

Run the server:

```bash
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## API Endpoints

### `POST /ask`
Submit a user question. Returns either a direct answer or a clarifying question.

**Request**
```json
{ "question": "How do I sort a list?" }
```

**Response (direct answer)**
```json
{
  "session_id": "abc-123",
  "decision": "answer",
  "uncertainty_score": 0.2,
  "reason": "Question is unambiguous.",
  "answer": "Use list.sort() or sorted(list)."
}
```

**Response (clarifying question)**
```json
{
  "session_id": "abc-123",
  "decision": "clarify",
  "uncertainty_score": 0.7,
  "reason": "Programming language is unspecified.",
  "clarifying_question": "Which programming language are you using?"
}
```

---

### `POST /clarify`
Submit a clarification for a previous `/ask` session.

**Request**
```json
{
  "session_id": "abc-123",
  "clarification": "I'm using Python."
}
```

**Response**
```json
{
  "session_id": "abc-123",
  "final_answer": "Use list.sort() for in-place sorting or sorted(list) for a new list.",
  "confidence": 0.95,
  "explanation": "Clarification resolved the language ambiguity."
}
```

---

### `POST /llm`
Pass a raw prompt directly to the LLM (utility/debug endpoint).

---

### `GET /logs`
Retrieve all session interaction logs for evaluation and analysis.

## Design Notes

Uncertainty is estimated via structured prompting — the LLM is instructed to reason through ambiguity, missing details, and risk of incorrect assumptions, then output a calibrated score. This is an epistemic uncertainty elicitation approach, as the Gemini API does not expose token-level log-probabilities.

Sessions are stored in memory and do not persist across server restarts.
