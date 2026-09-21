"""
Create/upgrade the database.

Safe to run against the existing healthsphere.db: SQLAlchemy's
`Base.metadata.create_all()` only creates tables that don't exist yet, so the
current users/patient_profiles/notifications/vitals_records/lab_reports/
assessment_results/care_plans tables and their data are left untouched. It
only adds the new tables: agent_tasks, chat_sessions, chat_messages,
escalation_tickets, medicine_recommendations.

Usage:
    python -m app.db.init_db
"""

from app.db.session import engine
from app.core.config import settings
from app.models.models import Base


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print(f"Database ready at {settings.DATABASE_URL}")
    print("Tables:", ", ".join(sorted(Base.metadata.tables.keys())))


if __name__ == "__main__":
    init_db()
