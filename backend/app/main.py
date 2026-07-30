import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base
from app.api import (
    auth, profile, dashboard, resume, github, linkedin,
    fusion, prediction, readiness, skill_gap, roadmap,
    shap, simulator, admin
)

# Auto-create tables on startup (useful for SQLite out of the box)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization warning: {e}")

app = FastAPI(
    title="AI-Based Career Intelligence & Placement Readiness API",
    description="Backend API providing placement probability prediction, ATS scoring, skill fusion, SHAP explanations, learning roadmaps, and admin controls.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(dashboard.router)
app.include_router(resume.router)
app.include_router(github.router)
app.include_router(linkedin.router)
app.include_router(fusion.router)
app.include_router(prediction.router)
app.include_router(readiness.router)
app.include_router(skill_gap.router)
app.include_router(roadmap.router)
app.include_router(shap.router)
app.include_router(simulator.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "AI-Based Career Intelligence & Placement Readiness API",
        "docs": "/docs",
        "version": "1.0.0"
    }
