import uuid
from typing import Optional

_sessions: dict = {}
_logs: list = []


def create_session(data: dict) -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = data
    _logs.append({"session_id": session_id, **data})
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    return _sessions.get(session_id)


def update_session(session_id: str, updates: dict) -> None:
    if session_id in _sessions:
        _sessions[session_id].update(updates)
        for i, log in enumerate(_logs):
            if log.get("session_id") == session_id:
                _logs[i] = {"session_id": session_id, **_sessions[session_id]}
                return


def get_logs() -> list:
    return _logs
