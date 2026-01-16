from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import user, task, team
from app.routes import auth
from app.routes import task as task_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

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

from app.routes import subtask
app.include_router(subtask.router, tags=["SubTasks"])

from app.routes import admin
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

from app.routes import team
app.include_router(team.router, prefix="/teams", tags=["Teams"])