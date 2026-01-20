from apscheduler.schedulers.background import BackgroundScheduler
from app.core.database import SessionLocal
from app.jobs.deadline_checker import _check_deadlines_once
import logging

logger = logging.getLogger(__name__)


def start_scheduler(interval_seconds: int = 300):
    """Start a BackgroundScheduler to run the deadline checker periodically."""
    sched = BackgroundScheduler()

    def _job():
        db = SessionLocal()
        try:
            _check_deadlines_once(db)
        except Exception as e:
            logger.exception("Scheduled deadline check failed: %s", e)
        finally:
            db.close()

    sched.add_job(_job, "interval", seconds=interval_seconds, id="deadline_checker", replace_existing=True)
    sched.start()
    logger.info("APScheduler started for deadline_checker every %s seconds", interval_seconds)
    return sched


def stop_scheduler(sched: BackgroundScheduler):
    try:
        sched.shutdown(wait=False)
        logger.info("APScheduler scheduler stopped")
    except Exception:
        pass
