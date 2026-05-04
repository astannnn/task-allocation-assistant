from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.services.reminder_service import run_deadline_check


scheduler = BackgroundScheduler()


def scheduled_deadline_check():
    """
    Scheduled job for checking approaching and overdue task deadlines.

    It opens its own database session because scheduled jobs run outside
    the normal FastAPI request lifecycle.
    """
    db = SessionLocal()

    try:
        run_deadline_check(db)
    finally:
        db.close()


def start_scheduler():
    """
    Start APScheduler if it is not already running.
    """
    if not scheduler.running:
        scheduler.add_job(
            scheduled_deadline_check,
            trigger="interval",
            minutes=60,
            id="deadline_check_job",
            replace_existing=True,
        )

        scheduler.start()


def shutdown_scheduler():
    """
    Stop APScheduler when the application shuts down.
    """
    if scheduler.running:
        scheduler.shutdown()