"""
ScholarSense FastAPI Application
Main entry point for the API server.
"""
import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from database import init_db
from logging_config import setup_logging
from routers import auth, documents, profiles, opportunities, materials

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="ScholarSense API",
    description="AI-powered application assistant for students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Middleware ---

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log incoming requests and their processing time."""
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path}")
    logger.info(f"Request Headers: {request.headers}")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Response: {response.status_code} - Process Time: {process_time:.2f}ms")
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handles and logs any unhandled exception."""
    logger.critical(f"Unhandled exception for {request.method} {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# --- Routers ---
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(profiles.router)
app.include_router(opportunities.router)
app.include_router(materials.router)


# --- Lifespan Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    logger.info("Database initialized")
    logger.info(f"Server starting on http://localhost:8000")
    logger.info(f"API docs available at http://localhost:8000/docs")


# --- Root and Health Check ---
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ScholarSense API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
