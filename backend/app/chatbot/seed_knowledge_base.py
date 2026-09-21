"""
Seed the RAG chatbot's knowledge base (ChromaDB collection: healthsphere_kb).

Two kinds of content go in here — keep them clearly separated by "source":
  - "app_faq": how to use HealthSphere itself (upload a report, read your
    dashboard, notification settings, etc.)
  - "health_education": general, non-personalized public-guideline summaries
    (e.g. "what is HbA1c", "general lifestyle tips for heart health"). These
    must stay generic — never phrased as advice for a specific person.

Run: python -m app.chatbot.seed_knowledge_base
"""

import chromadb

APP_FAQ_DOCS = [
    ("faq_upload_report", "To upload a lab report, go to your Patient Portal, "
     "click 'Upload Report', and choose a PDF or photo. Our OCR pipeline will "
     "extract the key values automatically within a minute."),
    ("faq_dashboard", "Your health timeline dashboard shows your past reports, "
     "risk trend lines, and upcoming reminders. Tap any point on the trend "
     "graph to see the report it came from."),
    ("faq_notifications", "You can manage reminder notifications under "
     "Settings > Notifications. You can turn on SMS, email, or in-app alerts."),
    ("faq_care_plan_approval", "A care plan only becomes active after your "
     "doctor reviews and approves it. You'll get a notification when that happens."),
    ("faq_password_reset", "To reset your password, click 'Forgot password' "
     "on the login screen. If you don't receive the reset email within a few "
     "minutes, check your spam folder or contact support."),
]

HEALTH_EDUCATION_DOCS = [
    ("edu_hba1c", "HbA1c is a blood test that reflects average blood sugar "
     "levels over roughly the past 2-3 months. It's commonly used to monitor "
     "diabetes management. Target ranges vary by individual and should be "
     "set with your doctor."),
    ("edu_blood_pressure", "Blood pressure is recorded as systolic/diastolic "
     "(e.g. 120/80 mmHg). Consistently elevated readings over time are one "
     "factor doctors consider when assessing cardiovascular risk."),
    ("edu_lifestyle_heart", "General, widely recommended heart-healthy habits "
     "include regular physical activity, balanced diet with limited sodium, "
     "not smoking, and regular checkups. This is general information, not a "
     "personal treatment plan."),
    ("edu_ckd_basics", "Chronic Kidney Disease (CKD) is often tracked using "
     "serum creatinine and estimated GFR. Early stages may have no symptoms, "
     "which is why routine screening matters for at-risk patients."),
]


def seed(host: str = "vector-store", port: int = 8001, collection_name: str = "healthsphere_kb"):
    client = chromadb.HttpClient(host=host, port=port)
    collection = client.get_or_create_collection(collection_name)

    all_docs = APP_FAQ_DOCS + HEALTH_EDUCATION_DOCS
    ids = [doc_id for doc_id, _ in all_docs]
    texts = [text for _, text in all_docs]
    metadatas = [
        {"source": "app_faq" if doc_id.startswith("faq_") else "health_education"}
        for doc_id, _ in all_docs
    ]

    collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
    print(f"Seeded {len(all_docs)} knowledge-base entries into '{collection_name}'.")


if __name__ == "__main__":
    seed()
