"""
HealthSphere Assistant — RAG Chatbot with Human-in-the-Loop Escalation
========================================================================

Pipeline:
  1. RETRIEVE — embed the user's question and pull the top-k relevant chunks
     from a local vector store (ChromaDB) built from:
       - the platform's own FAQ / how-to-use-the-app content   -> "technical"
       - general, non-personalized health-education material
         (public guideline summaries, NOT medical advice)      -> "clinical_info"
  2. GENERATE — call the LLM with ONLY the retrieved context (grounded
     answer), plus a system prompt that forbids diagnosis/prescription.
  3. GATE — before returning the generated answer, check:
       a) did the Patient Care Agent's red-flag screen already fire? -> escalate, don't answer
       b) is retrieval confidence below threshold?                  -> escalate to human
       c) did the user explicitly ask for a human / say the AI isn't helping? -> escalate
     "Escalate" = create an EscalationTicket (category="clinical" routes to a
     doctor, category="technical" routes to an engineer) and tell the user
     a human will follow up, instead of guessing.

This keeps the chatbot useful for FAQ/navigation/general info while making
sure anything that smells like "diagnose me" or "the app is broken and I
need a person" reliably reaches a human.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.agents.patient_agent import screen_message_for_red_flags
from app.models.models import ChatMessage, ChatSession, EscalationTicket

CONFIDENCE_ESCALATION_THRESHOLD = 0.45

HUMAN_HANDOFF_PHRASES = [
    "talk to a doctor", "talk to a human", "speak to someone",
    "this isn't working", "not helpful", "report a bug", "app is broken",
    "connect me with", "real person",
]

TECHNICAL_KEYWORDS = [
    "login", "log in", "password", "upload failed", "error", "crash",
    "app is broken", "report a bug", "notification not working", "sync",
]

SYSTEM_PROMPT = """You are the HealthSphere AI Assistant, a support chatbot for a clinical
decision-support platform. You may:
  - explain how to use the app (upload a report, read your dashboard, etc.)
  - explain general, publicly known health/education concepts in plain language
You must NOT:
  - diagnose the user's condition
  - recommend a specific medication or dosage
  - tell the user to start, stop, or change any treatment
If the user describes symptoms, personal risk, or asks "what's wrong with me" /
"what should I take", say you can't give personalized medical advice and that
you're flagging this for a clinician to follow up.
Answer ONLY using the provided context. If the context doesn't cover the
question, say so honestly rather than guessing.
"""


@dataclass
class RagAnswer:
    text: str
    confidence: float
    sources: list[str]
    escalated: bool
    ticket_id: int | None = None


class VectorStoreClient:
    """
    Thin wrapper around ChromaDB (see docker-compose 'vector-store' service).
    Swap this class if the team prefers pgvector / FAISS / Pinecone instead —
    nothing else in this file needs to change.
    """

    def __init__(self, host: str = "vector-store", port: int = 8001, collection: str = "healthsphere_kb"):
        import chromadb  # local import so this module is importable without chromadb during unit tests

        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.get_or_create_collection(collection)

    def query(self, question: str, top_k: int = 4) -> tuple[list[str], list[str], float]:
        results = self.collection.query(query_texts=[question], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0] or [1.0]
        # Convert distance -> a rough 0..1 confidence (smaller distance = more relevant)
        avg_distance = sum(distances) / len(distances)
        confidence = max(0.0, 1.0 - avg_distance)
        return docs, ids, confidence


def _call_llm(system_prompt: str, context_chunks: list[str], question: str) -> str:
    """
    Calls the Anthropic Claude API with the retrieved context. Requires
    ANTHROPIC_API_KEY in the environment (see backend/.env.example).
    """
    import os

    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    context_text = "\n---\n".join(context_chunks) if context_chunks else "(no matching context found)"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nUser question: {question}",
            }
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def _classify_escalation_category(message: str) -> str:
    lowered = message.lower()
    if any(k in lowered for k in TECHNICAL_KEYWORDS):
        return "technical"
    return "clinical"


def _create_escalation(
    db: Session,
    session: ChatSession,
    reason: str,
    summary: str,
    urgency: str = "normal",
) -> EscalationTicket:
    category = _classify_escalation_category(summary)
    ticket = EscalationTicket(
        patient_id=getattr(session.user, "patient_profile", None) and session.user.patient_profile.id,
        chat_session_id=session.id,
        category=category,
        reason=reason,
        summary=summary[:500],
        urgency=urgency,
        assigned_role="doctor" if category == "clinical" else "engineer",
        status="open",
        created_at=datetime.utcnow(),
    )
    db.add(ticket)
    session.status = "escalated"
    db.commit()
    db.refresh(ticket)
    return ticket


def answer_user_message(
    db: Session,
    session: ChatSession,
    user_message: str,
    vector_store: VectorStoreClient | None = None,
) -> RagAnswer:
    """Main entry point called by the chat API route."""

    db.add(ChatMessage(session_id=session.id, role="user", content=user_message, created_at=datetime.utcnow()))
    db.commit()

    # --- Gate 1: red-flag symptom screen (shared with the Patient Care Agent) ---
    patient_id = session.user.patient_profile.id if getattr(session.user, "patient_profile", None) else None
    if screen_message_for_red_flags(user_message):
        ticket = _create_escalation(
            db, session, reason="red_flag_symptom",
            summary=f"Urgent symptom description: \"{user_message[:300]}\"",
            urgency="emergency",
        )
        reply = (
            "This sounds like it could be urgent. I'm not able to assess symptoms like this myself, "
            "so I've flagged it for a clinician to reach out right away. "
            "If this is a medical emergency, please contact emergency services or go to the nearest "
            "emergency room immediately."
        )
        _save_assistant_message(db, session, reply, confidence=1.0, sources=[], escalated=True)
        return RagAnswer(text=reply, confidence=1.0, sources=[], escalated=True, ticket_id=ticket.id)

    # --- Gate 2: explicit human handoff request ---
    if any(p in user_message.lower() for p in HUMAN_HANDOFF_PHRASES):
        ticket = _create_escalation(
            db, session, reason="user_requested",
            summary=f"User asked to speak with a human: \"{user_message[:300]}\"",
            urgency="normal",
        )
        reply = "Of course — I've routed this to our team and someone will follow up with you shortly."
        _save_assistant_message(db, session, reply, confidence=1.0, sources=[], escalated=True)
        return RagAnswer(text=reply, confidence=1.0, sources=[], escalated=True, ticket_id=ticket.id)

    # --- Retrieve ---
    store = vector_store or VectorStoreClient()
    docs, ids, confidence = store.query(user_message)

    # --- Gate 3: low retrieval confidence -> escalate instead of hallucinating ---
    if confidence < CONFIDENCE_ESCALATION_THRESHOLD or not docs:
        ticket = _create_escalation(
            db, session, reason="low_confidence",
            summary=f"Low-confidence question ({confidence:.2f}): \"{user_message[:300]}\"",
            urgency="normal",
        )
        reply = (
            "I don't have a confident, sourced answer for that. I've forwarded your question to our "
            "clinical/support team so a person can follow up with you directly."
        )
        _save_assistant_message(db, session, reply, confidence=confidence, sources=[], escalated=True)
        return RagAnswer(text=reply, confidence=confidence, sources=[], escalated=True, ticket_id=ticket.id)

    # --- Generate grounded answer ---
    answer_text = _call_llm(SYSTEM_PROMPT, docs, user_message)
    _save_assistant_message(db, session, answer_text, confidence=confidence, sources=ids, escalated=False)
    return RagAnswer(text=answer_text, confidence=confidence, sources=ids, escalated=False)


def _save_assistant_message(db: Session, session: ChatSession, text: str, confidence: float, sources: list[str], escalated: bool) -> None:
    db.add(
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content=text,
            retrieved_sources=sources,
            confidence=confidence,
            was_escalated=escalated,
            created_at=datetime.utcnow(),
        )
    )
    session.last_active_at = datetime.utcnow()
    db.commit()
