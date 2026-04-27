import re
import spacy

_nlp = spacy.load("en_core_web_sm")

# ─────────────────────────────────────────────
# Taxonomy: question types and their required slots
# ─────────────────────────────────────────────
QUESTION_TAXONOMY = {
    "comparison": {
        "description": "Compares two or more things",
        "required_slots": ["entity_1", "entity_2", "dimension"],
        "trigger_words": ["vs", "versus", "difference between", "compare"],
    },
    "recommendation": {
        "description": "Asks for a suggestion or best option",
        "required_slots": ["domain", "constraints"],
        "trigger_words": ["best", "recommend", "should i buy", "which one should", "suggest", "good for", "what to buy"],
    },
    "procedural": {
        "description": "Asks how to do something",
        "required_slots": ["task", "context"],
        "trigger_words": ["how to", "how do i", "how can i", "steps to", "way to"],
    },
    "location": {
        "description": "Asks about a place or where something is",
        "required_slots": ["subject", "location_context"],
        "trigger_words": ["near me", "in my area", "closest", "nearby"],
    },
    "temporal": {
        "description": "Asks about time, dates, or schedules",
        "required_slots": ["subject", "time_reference"],
        "trigger_words": ["when does", "when did", "when will", "what time", "how long", "how often", "schedule"],
    },
    "factual": {
        "description": "Seeks a specific, objective fact",
        "required_slots": ["subject"],
        "trigger_words": ["what is", "who is", "where is", "how many", "which", "what", "who", "where", "when"],
    },
}

# ─────────────────────────────────────────────
# Rules: structural checks on the question
# ─────────────────────────────────────────────

def _detect_question_type(question: str) -> str:
    q = question.lower()
    for qtype, meta in QUESTION_TAXONOMY.items():
        for trigger in meta["trigger_words"]:
            if trigger in q:
                return qtype
    return "factual"  # default


def _check_missing_slots(question: str, qtype: str, doc) -> list[str]:
    missing = []
    entities = [ent.text for ent in doc.ents]
    q = question.lower()

    if qtype == "factual":
        if not entities and len(doc) < 5:
            missing.append("subject")

    elif qtype == "comparison":
        if len(entities) < 2:
            missing.append("entity_1 and/or entity_2")
        dimension_words = ["price", "size", "speed", "quality", "performance", "cost", "better", "worse"]
        if not any(w in q for w in dimension_words):
            missing.append("comparison dimension")

    elif qtype == "recommendation":
        if not entities and not any(w in q for w in ["for", "to", "about"]):
            missing.append("domain")
        constraint_words = ["cheap", "fast", "easy", "best", "top", "affordable", "reliable", "for"]
        if not any(w in q for w in constraint_words):
            missing.append("constraints or preferences")

    elif qtype == "procedural":
        if not entities and len(doc) < 6:
            missing.append("task context")

    elif qtype == "location":
        location_entities = [ent for ent in doc.ents if ent.label_ in ("GPE", "LOC", "FAC")]
        if not location_entities:
            missing.append("location context")

    elif qtype == "temporal":
        time_entities = [ent for ent in doc.ents if ent.label_ in ("DATE", "TIME", "EVENT")]
        time_words = ["today", "now", "current", "latest", "next", "last", "recent"]
        if not time_entities and not any(w in q for w in time_words):
            missing.append("time reference")
        non_time_entities = [ent for ent in doc.ents if ent.label_ not in ("DATE", "TIME")]
        subject_nouns = [t for t in doc if t.pos_ in ("NOUN", "PROPN") and t.text.lower() not in time_words]
        if not non_time_entities and not subject_nouns:
            missing.append("subject")

    return missing


def _compute_uncertainty_contribution(missing_slots: list[str], qtype: str) -> float:
    if not missing_slots:
        return 0.0
    base = 0.3
    per_slot = 0.2
    score = base + per_slot * len(missing_slots)
    return min(score, 0.9)


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def assess_question(question: str) -> dict:
    """
    Run the question through the KB and return a structured pre-assessment.
    This is passed to the LLM as context before it makes its own judgment.
    """
    doc = _nlp(question)
    qtype = _detect_question_type(question)
    missing = _check_missing_slots(question, qtype, doc)
    kb_uncertainty = _compute_uncertainty_contribution(missing, qtype)
    entities = [ent.text for ent in doc.ents]

    return {
        "question_type": qtype,
        "detected_entities": entities,
        "missing_slots": missing,
        "kb_uncertainty_score": kb_uncertainty,
        "taxonomy_description": QUESTION_TAXONOMY[qtype]["description"],
        "required_slots": QUESTION_TAXONOMY[qtype]["required_slots"],
    }
