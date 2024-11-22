from fastapi import HTTPException, UploadFile
from app.schemas.processing import ProcessingConfig
import os
import pandas as pd

ALLOWED_EXTENSIONS = {'.csv', '.json', '.txt', '.xlsx'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

SUPPORTED_TRANSFORMATIONS = {
    'tokenization',
    'stopword_removal',
    'lemmatization',
    'stemming',
    'named_entity_recognition',
    'pos_tagging',
    'text_vectorization'
}

async def validate_file(file: UploadFile) -> None:
    """
    Validate the uploaded file.
    
    Args:
        file: The uploaded file to validate
    
    Raises:
        HTTPException: If the file is invalid
    """
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # Try to read the file with pandas
    try:
        if ext == '.csv':
            pd.read_csv(file.file)
        elif ext == '.json':
            pd.read_json(file.file)
        elif ext == '.xlsx':
            pd.read_excel(file.file)
        elif ext == '.txt':
            pd.read_csv(file.file, sep='\t')
        
        await file.seek(0)  # Reset file pointer again
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format: {str(e)}"
        )

def validate_config(config: ProcessingConfig) -> None:
    """
    Validate the processing configuration.
    
    Args:
        config: The processing configuration to validate
    
    Raises:
        HTTPException: If the configuration is invalid
    """
    # Validate transformations
    for transform in config.transformations:
        if transform.type not in SUPPORTED_TRANSFORMATIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported transformation: {transform.type}"
            )
        
        # Validate transformation-specific parameters
        if transform.type == 'text_vectorization':
            if 'method' not in transform.params:
                raise HTTPException(
                    status_code=400,
                    detail="text_vectorization requires 'method' parameter"
                )
            if transform.params['method'] not in ['tfidf', 'count']:
                raise HTTPException(
                    status_code=400,
                    detail="text_vectorization method must be 'tfidf' or 'count'"
                )
    
    # Validate batch size
    if config.batch_size is not None and config.batch_size <= 0:
        raise HTTPException(
            status_code=400,
            detail="batch_size must be positive"
        )
