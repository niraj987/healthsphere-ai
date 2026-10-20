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

SYSTEM_PROMPT = """You are the Smart Hospital Assistant, a support chatbot for a clinical
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
    Thin wrapper around ChromaDB.
    Attempts to connect to remote HttpClient, falls back to in-memory Client with seeded KB.
    """

    DEFAULT_DOCS = [
        {
            "id": "faq_upload_lab",
            "text": "To upload a lab report on Smart Hospital Management: Navigate to the Medical Records or Patient Dashboard tab, click 'Upload Lab Report', select your PDF or image file (CBC, Metabolic Panel, Lipid Panel), and click submit. Our OCR engine automatically extracts biomarkers and logs your vitals."
        },
        {
            "id": "faq_vitals_tracking",
            "text": "To record daily vitals: Go to Patient Dashboard -> Vitals section, click 'Log Vitals', enter your Systolic BP, Diastolic BP, Heart Rate, Fasting Glucose, or Serum Creatinine, and save. Vitals feed directly into the AI Risk Assessment engine."
        },
        {
            "id": "faq_care_plans",
            "text": "Care plans are personalized clinical summaries created by AI and reviewed by your attending physician. Once a doctor approves your care plan, you can view prescriptions, lifestyle recommendations, and follow-up dates under 'Care Plans'."
        },
        {
            "id": "clinical_hypertension_info",
            "text": "Hypertension (high blood pressure) is defined as systolic blood pressure >= 130 mmHg or diastolic >= 80 mmHg. Lifestyle modifications include reduced sodium intake, regular cardiovascular exercise, stress management, and prescribed antihypertensive medications under physician supervision."
        },
        {
            "id": "clinical_diabetes_info",
            "text": "Type 2 Diabetes management involves monitoring fasting blood glucose (normal < 100 mg/dL, diabetic >= 126 mg/dL) and HbA1c (normal < 5.7%, diabetic >= 6.5%). Patients should follow a balanced dietary plan, maintain active exercise, and track glucose regularly."
        },
        {
            "id": "clinical_ckd_info",
            "text": "Chronic Kidney Disease (CKD) risk is evaluated using serum creatinine, eGFR, and blood pressure. Early detection requires monitoring kidney function biomarkers, managing blood pressure, and avoiding nephrotoxic substances."
        }
    ]

    def __init__(self, host: str = "vector-store", port: int = 8001, collection: str = "healthsphere_kb"):
        import chromadb

        try:
            self.client = chromadb.HttpClient(host=host, port=port)
            self.collection = self.client.get_or_create_collection(collection)
        except Exception:
            # Fallback to local in-memory ChromaDB client
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(collection)
            self._seed_default_kb()

    def _seed_default_kb(self):
        try:
            existing = self.collection.get()
            if not existing.get("ids"):
                ids = [doc["id"] for doc in self.DEFAULT_DOCS]
                texts = [doc["text"] for doc in self.DEFAULT_DOCS]
                self.collection.add(ids=ids, documents=texts)
        except Exception:
            pass

    def query(self, question: str, top_k: int = 4) -> tuple[list[str], list[str], float]:
        q_lower = question.lower()
        matched_docs = []
        matched_ids = []

        # Keyword matching directly against default KB first to gauge direct relevance
        for doc in self.DEFAULT_DOCS:
            if any(word in doc["text"].lower() for word in q_lower.split() if len(word) > 3):
                matched_docs.append(doc["text"])
                matched_ids.append(doc["id"])

        try:
            results = self.collection.query(query_texts=[question], n_results=top_k)
            docs = results.get("documents", [[]])[0]
            ids = results.get("ids", [[]])[0]
            
            if docs:
                confidence = 0.85 if matched_docs else 0.70
                return docs, ids, confidence
        except Exception:
            pass

        confidence = 0.85 if matched_docs else 0.20
        return matched_docs, matched_ids, confidence


def _call_llm(system_prompt: str, context_chunks: list[str], question: str) -> str:
    """
    Calls Anthropic Claude API if key present, else synthesizes grounded response from retrieved context.
    """
    import os

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key and api_key.startswith("sk-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            context_text = "\n---\n".join(context_chunks) if context_chunks else "(no matching context found)"
            
            try:
                response = client.messages.create(
                    model="claude-3-7-sonnet-latest",
                    max_tokens=500,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Context:\n{context_text}\n\nUser question: {question}",
                        }
                    ],
                )
            except Exception:
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
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
        except Exception as err:
            pass

    # Grounded fallback synthesizer using retrieved knowledge chunks
    if not context_chunks:
        return "I couldn't find specific information regarding your request in the Smart Hospital Management knowledge base."
    
    primary_info = "\n\n".join(context_chunks[:2])
    return f"Based on Smart Hospital Management clinical and platform guidance:\n\n{primary_info}\n\n*Note: This information is for general educational & navigation purposes. Please consult your physician for personalized medical advice.*"



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
