"""
Maintenance Wizard - FastAPI Backend
Run: uvicorn main:app --reload --port 8000
"""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from rag_routes import router as rag_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Maintenance Wizard API starting...")
    yield
    logger.info("⛔ Maintenance Wizard API shutting down")


app = FastAPI(
    title="Maintenance Wizard API",
    description="Intelligent maintenance decision-support for steel plant equipment",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for React frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://maintenance-wizard.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(rag_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "maintenance-wizard"}


@app.get("/")
async def root():
    return {
        "name": "Maintenance Wizard API",
        "docs": "/docs",
        "health": "/health",
    }
