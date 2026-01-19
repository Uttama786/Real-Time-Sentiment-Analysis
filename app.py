"""
Main FastAPI application
"""
import os
import logging
from fastapi import FastAPI
from dotenv import load_dotenv

from api.routes import router
from api.middleware import setup_middleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sentiment Analysis API",
    description="Real-time sentiment analysis API",
    version="1.0.0"
)

# Setup middleware
setup_middleware(app)

# Include router
app.include_router(router)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Sentiment Analysis API...")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Sentiment Analysis API...")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
