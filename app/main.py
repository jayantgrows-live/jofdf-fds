from fastapi import FastAPI, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
from app.auth.api_key import get_api_key

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with docs disabled
app = FastAPI(
    title="Voice Note AI",
    description="AI-powered voice note transcription and analysis API",
    version="1.0.0",
    docs_url=None,    # Disable Swagger UI
    redoc_url=None,   # Disable ReDoc
    openapi_url=None  # Disable OpenAPI schema
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {"message": "Server is running"}

# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import routers after app creation to avoid circular imports
from app.routers import voice_notes, youtube_notes

# Include routers with authentication
app.include_router(
    voice_notes.router,
    prefix="/api/v1",
    tags=["voice-notes"],
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    youtube_notes.router,
    prefix="/api/v1",
    tags=["youtube-notes"],
    dependencies=[Depends(get_api_key)]
) 