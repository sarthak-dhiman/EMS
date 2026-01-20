from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from app.core.database import Base, engine
from app.models import task, team, user, notification
from app.routes import admin, auth, subtask, notification as notification_router
from app.routes import task as task_router
from app.routes import team as team_router
from app.core.exceptions import add_exception_handlers
from app.core.logging_config import logger
# Database initialization is now handled via Alembic migrations in start.sh
# Base.metadata.create_all(bind=engine)
from app.middleware.rate_limiter import SimpleRateLimitMiddleware
from app.jobs.deadline_checker import start_in_thread
# Scheduler (APScheduler) is optional. If available, prefer it for more robust scheduling.
try:
    from app.jobs.scheduler import start_scheduler, stop_scheduler
    _HAS_SCHEDULER = True
except Exception:
    _HAS_SCHEDULER = False
import os

app = FastAPI()

# Attach simple rate limiter (in-memory). Tune via RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW_SECONDS.
app.add_middleware(SimpleRateLimitMiddleware)

print("--- APP STARTUP: LOGGING INITIALIZED ---") # Sanity check for stdout

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000  # ms
    
    # Log the request details
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(process_time, 2),
        "ip": request.client.host
    }
    
    logger.info(
        f"{request.method} {request.url.path} completed in {process_time:.2f}ms | Status: {response.status_code}",
        extra=log_data
    )
    
    return response

# Register global exception handlers
add_exception_handlers(app)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/")
def health_check():
    return {"status": "System is running"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(task_router.router, prefix="/tasks", tags=["Tasks"])
app.include_router(subtask.router, tags=["SubTasks"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(team_router.router, prefix="/teams", tags=["Teams"])
app.include_router(notification_router.router, prefix="/notifications", tags=["Notifications"])
from app.routes import report as report_router
app.include_router(report_router.router, prefix="/reports", tags=["Reports"])


@app.on_event("startup")
def _start_background_jobs():
    # Start the deadline checker thread if enabled via env
    try:
        if os.getenv("ENABLE_DEADLINE_CHECKER", "true").lower() in ("1", "true", "yes"):
            interval = int(os.getenv("DEADLINE_CHECKER_INTERVAL_SECONDS", "300"))
            if _HAS_SCHEDULER:
                try:
                    app.state._apscheduler = start_scheduler(interval_seconds=interval)
                    logger.info("APScheduler deadline checker started with interval %s seconds", interval)
                except Exception:
                    # Fallback to simple thread if scheduler fails
                    app.state._deadline_stop = start_in_thread(interval_seconds=interval)
                    logger.info("Fallback deadline checker thread started with interval %s seconds", interval)
            else:
                app.state._deadline_stop = start_in_thread(interval_seconds=interval)
                logger.info("Deadline checker started with interval %s seconds", interval)
    except Exception as e:
        logger.exception("Failed to start background jobs: %s", e)


@app.on_event("shutdown")
def _stop_background_jobs():
    try:
        stop = getattr(app.state, "_deadline_stop", None)
        if stop:
            stop.set()
            logger.info("Deadline checker stop requested")
        sched = getattr(app.state, "_apscheduler", None)
        if sched:
            try:
                stop_scheduler(sched)
            except Exception:
                pass
    except Exception:
        pass
