"""
Background scheduler for the two AI agents. Runs as its own container
(see 'agent-worker' service in docker-compose.yml) so periodic jobs never
block the request/response FastAPI process.

Jobs:
  - every 15 min: refresh the Clinician Assist Agent's prioritized worklist
    cache (so the Doctor Dashboard loads instantly)
  - every hour: Patient Care Agent scans for overdue AgentTasks and drafts
    adherence nudges
  - once a day (06:00): Patient Care Agent builds each patient's daily digest
    and queues a notification

Run: python -m app.agents.worker
"""

from __future__ import annotations

import logging
import os
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents import doctor_agent, patient_agent
from app.models.models import AgentTask, PatientProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("healthsphere.agent_worker")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./healthsphere.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def refresh_worklist_job():
    db = SessionLocal()
    try:
        worklist = doctor_agent.build_prioritized_worklist(db)
        logger.info("Refreshed clinician worklist: %d patients ranked", len(worklist))
        # In production: write this to Redis (REDIS_URL) so the Doctor
        # Dashboard API can serve it without recomputing on every request.
    finally:
        db.close()


def adherence_check_job():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        overdue_tasks = (
            db.query(AgentTask)
            .filter(AgentTask.status == "pending", AgentTask.scheduled_for < now)
            .all()
        )
        for task in overdue_tasks:
            patient_agent.draft_adherence_nudge(db, task.patient_id, task)
        logger.info("Adherence check: nudged %d overdue task(s)", len(overdue_tasks))
    finally:
        db.close()


def daily_digest_job():
    db = SessionLocal()
    try:
        patients = db.query(PatientProfile).all()
        for patient in patients:
            digest = patient_agent.build_daily_digest(db, patient.id)
            logger.info("Daily digest for patient %s: %s", patient.id, digest.plain_summary)
            # In production: push via Notification row + Twilio/email service.
    finally:
        db.close()


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(refresh_worklist_job, "interval", minutes=15, id="refresh_worklist")
    scheduler.add_job(adherence_check_job, "interval", hours=1, id="adherence_check")
    scheduler.add_job(daily_digest_job, "cron", hour=6, minute=0, id="daily_digest")
    logger.info("Agent worker started. Jobs: %s", [j.id for j in scheduler.get_jobs()])
    scheduler.start()


if __name__ == "__main__":
    main()
