import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.db.database import init_db
from backend.api.routes_overview import router as overview_router
from backend.api.routes_cases import router as cases_router
from backend.api.routes_systems import router as systems_router
from backend.api.routes_runs import router as runs_router
from backend.api.routes_eval import router as eval_router
from backend.api.routes_exports import router as exports_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Data Deletion Audit Platform — HackerRank Orchestrate October 2026",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(overview_router, prefix=settings.API_PREFIX, tags=["Overview"])
app.include_router(cases_router, prefix=settings.API_PREFIX, tags=["Cases"])
app.include_router(systems_router, prefix=settings.API_PREFIX, tags=["Systems"])
app.include_router(runs_router, prefix=settings.API_PREFIX, tags=["Runs"])
app.include_router(eval_router, prefix=settings.API_PREFIX, tags=["Evaluation"])
app.include_router(exports_router, prefix=settings.API_PREFIX, tags=["Exports"])

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
