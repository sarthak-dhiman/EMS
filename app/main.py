from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from app.core.database import Base, engine
from app.models import task, team, user
from app.routes import admin, auth, subtask
from app.routes import task as task_router
from app.routes import team as team_router
from app.core.exceptions import add_exception_handlers
from app.core.logging_config import logger
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

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