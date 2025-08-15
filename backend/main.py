"""
FastAPI main application for AI Recruitr backend
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.api.routes import router as api_router
from config.settings import settings, validate_settings
import time

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_recruitr.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Recruitr API",
    description="Smart Resume Matcher using FAISS + Langchain",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()

    # Log request
    logger.info(
        f"📥 {request.method} {request.url.path} - Client: {request.client.host}")

    try:
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.2f}s")

        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )


# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["AI Recruitr API"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 AI Recruitr API is running!",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": time.time()}


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    try:
        logger.info("🚀 Starting AI Recruitr API...")

        # Validate configuration
        validate_settings()

        # Initialize services (they're loaded when imported)
        logger.info("✅ All services initialized successfully")
        logger.info(
            f"🌐 API running on http://{settings.API_HOST}:{settings.API_PORT}")
        logger.info(
            f"📚 API docs available at http://{settings.API_HOST}:{settings.API_PORT}/docs")

    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("🛑 Shutting down AI Recruitr API...")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        f"Unhandled exception on {request.method} {request.url}: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )


def run_server():
    """Run the FastAPI server"""
    try:
        logger.info("Starting AI Recruitr FastAPI server...")

        uvicorn.run(
            "backend.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.API_RELOAD,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )

    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

# Register exception handlers on the app
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )
if __name__ == "__main__":
    run_server()