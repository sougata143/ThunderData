import json
import os
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def update_processing_status(file_id: str, status: str, message: str, progress: Optional[float] = None) -> None:
    """Update the processing status for a file.
    
    Args:
        file_id: The ID of the file being processed
        status: Current status (processing, completed, error)
        message: Status message
        progress: Optional progress percentage (0-100)
    """
    try:
        logger.debug(f"Updating status for file {file_id}: {status} - {message} ({progress}%)")
        
        # Create processed directory if it doesn't exist
        processed_dir = "processed"
        if not os.path.exists(processed_dir):
            logger.debug(f"Creating processed directory: {processed_dir}")
            os.makedirs(processed_dir)
        
        # Update status file
        status_file = os.path.join(processed_dir, f"processing_{file_id}.json")
        logger.debug(f"Writing status to file: {status_file}")
        
        status_data = {
            "status": status,
            "message": message,
            "progress": progress
        }
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
        
        logger.debug(f"Successfully updated status for file {file_id}")
        
    except Exception as e:
        logger.error(f"Error updating status for file {file_id}: {str(e)}")
        raise e

def get_processing_status(file_id: str) -> Dict[str, Any]:
    """Get the current processing status for a file.
    
    Args:
        file_id: The ID of the file to check
        
    Returns:
        Dict containing status information
    """
    try:
        logger.debug(f"Getting status for file {file_id}")
        
        # Check if file is still processing
        processing_file = os.path.join("processed", f"processing_{file_id}.json")
        logger.debug(f"Looking for status file: {processing_file}")
        
        if os.path.exists(processing_file):
            logger.debug(f"Found status file: {processing_file}")
            with open(processing_file, 'r') as f:
                status = json.load(f)
            logger.debug(f"Status content: {status}")
            return {
                "file_id": file_id,
                "status": status["status"],
                "message": status.get("message", "Processing in progress"),
                "progress": status.get("progress", 0)
            }
        
        # Check if processing is complete
        processed_dir = "processed"
        logger.debug(f"Checking processed directory: {processed_dir}")
        
        if os.path.exists(processed_dir):
            for filename in os.listdir(processed_dir):
                if filename.startswith(f"processed_{file_id}"):
                    logger.debug(f"Found processed file: {filename}")
                    # Remove the status file since processing is complete
                    if os.path.exists(processing_file):
                        os.remove(processing_file)
                    
                    return {
                        "file_id": file_id,
                        "status": "completed",
                        "message": "Processing complete",
                        "result_file": filename
                    }
        
        logger.debug(f"No status found for file {file_id}")
        return {
            "file_id": file_id,
            "status": "not_found",
            "message": "File not found or processing hasn't started"
        }
        
    except Exception as e:
        logger.error(f"Error getting status for file {file_id}: {str(e)}")
        raise e
