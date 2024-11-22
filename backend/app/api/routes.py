from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import os
import json
import logging
from app.schemas.processing import ProcessingConfig, ProcessingResponse
from app.core.processor import process_file
from app.utils.validation import validate_file, validate_config
from app.utils.status import update_processing_status, get_processing_status

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=ProcessingResponse)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload a file for processing."""
    try:
        # Validate file
        await validate_file(file)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{file_id}_{timestamp}{original_extension}"
        
        # Save file
        file_path = os.path.join("uploads", safe_filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "file_id": file_id,
            "filename": safe_filename,
            "status": "uploaded",
            "message": "File uploaded successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/process/{file_id}", response_model=ProcessingResponse)
async def process_data(
    file_id: str,
    config: ProcessingConfig,
    background_tasks: BackgroundTasks
):
    """Process an uploaded file with specified transformations."""
    try:
        # Find the uploaded file
        uploads_dir = "uploads"
        file_path = None
        for filename in os.listdir(uploads_dir):
            if filename.startswith(file_id):
                file_path = os.path.join(uploads_dir, filename)
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Validate configuration
        validate_config(config)
        
        # Generate output filename
        output_filename = f"processed_{os.path.basename(file_path)}"
        output_path = os.path.join("processed", output_filename)
        
        # Initialize processing status
        update_processing_status(
            file_id=file_id,
            status="processing",
            message="Processing started",
            progress=0
        )
        
        # Process file in background
        background_tasks.add_task(
            process_file,
            file_path,
            output_path,
            config.dict()
        )
        
        return {
            "file_id": file_id,
            "status": "processing",
            "message": "Processing started",
            "result_file": output_filename
        }
    
    except Exception as e:
        # Update status to error if something goes wrong
        update_processing_status(
            file_id=file_id,
            status="error",
            message=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{file_id}", response_model=ProcessingResponse)
async def get_status(file_id: str):
    """Get the processing status of a file."""
    try:
        logger.debug(f"Getting status for file_id: {file_id}")
        
        # Check if processing file exists
        processing_file = os.path.join("processed", f"processing_{file_id}.json")
        logger.debug(f"Looking for processing file: {processing_file}")
        
        if os.path.exists(processing_file):
            logger.debug(f"Found processing file: {processing_file}")
            with open(processing_file, 'r') as f:
                status = json.load(f)
            logger.debug(f"Status content: {status}")
            return {
                "file_id": file_id,
                "status": status.get("status", "processing"),
                "message": status.get("message", "Processing in progress"),
                "progress": status.get("progress", 0)
            }
        
        # Check if processed file exists
        processed_dir = "processed"
        logger.debug(f"Checking processed directory: {processed_dir}")
        processed_files = os.listdir(processed_dir)
        logger.debug(f"Found files in processed directory: {processed_files}")
        
        for filename in processed_files:
            if filename.startswith(f"processed_{file_id}"):
                logger.debug(f"Found processed file: {filename}")
                return {
                    "file_id": file_id,
                    "status": "completed",
                    "message": "Processing complete",
                    "result_file": filename
                }
        
        # No status found
        logger.debug(f"No status found for file_id: {file_id}")
        raise HTTPException(
            status_code=404,
            detail=f"No status found for file ID: {file_id}"
        )
    
    except Exception as e:
        logger.error(f"Error getting status for file_id {file_id}: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/download/{filename}")
async def download_file(filename: str):
    """Download a processed file."""
    file_path = os.path.join("processed", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )
