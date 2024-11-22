from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="ThunderData API",
    description="API for text data processing and transformation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for processed data downloads
app.mount("/downloads", StaticFiles(directory="processed"), name="downloads")

# Include API routes
app.include_router(api_router, prefix="/api")

# Create necessary directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
