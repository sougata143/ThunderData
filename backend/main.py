from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import pandas as pd
import json
import uuid
import os
from pathlib import Path

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for storing files
UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Store processing status
processing_status = {}

@app.post("/api/upload")
async def upload_file(file: UploadFile):
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Get file extension
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['csv', 'json', 'txt']:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Save file
        file_path = UPLOAD_DIR / f"{file_id}.{file_extension}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Initialize processing status
        processing_status[file_id] = {
            "status": "uploaded",
            "error": None,
            "result_file": None
        }
        
        return {"file_id": file_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/{file_id}")
async def process_file(file_id: str, config: Dict):
    try:
        # Validate file_id
        file_paths = list(UPLOAD_DIR.glob(f"{file_id}.*"))
        if not file_paths:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = file_paths[0]
        
        # Update status to processing
        processing_status[file_id] = {
            "status": "processing",
            "error": None,
            "result_file": None
        }
        
        # Read file based on extension
        extension = file_path.suffix.lower()
        if extension == '.csv':
            df = pd.read_csv(file_path)
        elif extension == '.json':
            df = pd.read_json(file_path)
        elif extension == '.txt':
            with open(file_path, 'r') as f:
                content = f.read()
            df = pd.DataFrame({'text': content.split('\n')})
        
        # Validate input column
        if config['input_column'] not in df.columns:
            raise HTTPException(status_code=400, detail=f"Input column '{config['input_column']}' not found in file")
        
        # Process transformations
        for transform in config['transformations']:
            transform_type = transform['type']
            params = transform['params']
            
            # Validate columns exist
            for col in params['columns']:
                if col not in df.columns:
                    raise HTTPException(status_code=400, detail=f"Column '{col}' not found in file")
            
            # Apply transformation
            if transform_type == 'remove_stopwords':
                # Implementation placeholder
                pass
            elif transform_type == 'vectorize':
                # Implementation placeholder
                pass
            elif transform_type == 'extract_entities':
                # Implementation placeholder
                pass
        
        # Save processed file
        result_file = f"{file_id}_processed.csv"
        result_path = PROCESSED_DIR / result_file
        df.to_csv(result_path, index=False)
        
        # Update status to completed
        processing_status[file_id] = {
            "status": "completed",
            "error": None,
            "result_file": result_file
        }
        
        return {"status": "success"}
    
    except Exception as e:
        processing_status[file_id] = {
            "status": "error",
            "error": str(e),
            "result_file": None
        }
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{file_id}")
async def get_status(file_id: str):
    if file_id not in processing_status:
        raise HTTPException(status_code=404, detail="File ID not found")
    
    return processing_status[file_id]

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = PROCESSED_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)
