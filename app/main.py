from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from app.database import engine
from app.routers import comments, labels, projects, tasks, users

app = FastAPI(
    title="TaskFlow API",
    version="1.0.0",
    description="REST API для управления задачами команды",
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(labels.router)
app.include_router(tasks.router)
app.include_router(comments.router)


@app.get("/health")
def health() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database connection failed") from None
    return {"status": "ok", "database": "up"}
