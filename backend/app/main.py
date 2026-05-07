from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import auth

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
