"""
ScholarSense FastAPI Application
Main entry point for the API server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from database import init_db
from routers import auth, documents, profiles, opportunities, materials

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="ScholarSense API",
    description="AI-powered application assistant for students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(profiles.router)
app.include_router(opportunities.router)
app.include_router(materials.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✅ Database initialized")
    print(f"✅ Server starting on http://localhost:8000")
    print(f"📚 API docs available at http://localhost:8000/docs")


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
