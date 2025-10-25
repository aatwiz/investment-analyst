"""
FastAPI Backend for Investment Analyst AI Agent
Main application entry point
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from pathlib import Path
import shutil
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from api.routes import files, analysis, modeling, reports, llm_analysis, search, companies, market
from utils.config import settings
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered investment analysis platform with semantic search",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
def create_directories():
    """Create necessary directories for file storage"""
    dirs = [
        settings.UPLOAD_DIR,
        settings.PROCESSED_DIR,
        settings.OUTPUT_DIR,
        "logs",
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    logger.info("Directories created successfully")

create_directories()

# Include routers
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(llm_analysis.router, prefix="/api/v1/llm", tags=["LLM Analysis"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Semantic Search"])
app.include_router(modeling.router, prefix="/api/v1/modeling", tags=["Modeling"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(companies.router, prefix="/api/v1", tags=["Companies & Deals"])
app.include_router(market.router, prefix="/api/v1/market", tags=["Market Research"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Investment Analyst AI Agent API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "upload_dir_exists": Path(settings.UPLOAD_DIR).exists(),
        "processed_dir_exists": Path(settings.PROCESSED_DIR).exists(),
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(f"Shutting down {settings.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
