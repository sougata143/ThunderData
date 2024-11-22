from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TextTransformation(BaseModel):
    type: str = Field(..., description="Type of text transformation")
    params: Optional[Dict[str, Any]] = Field(default={}, description="Parameters for the transformation")

class ProcessingConfig(BaseModel):
    transformations: List[TextTransformation] = Field(
        ...,
        description="List of text transformations to apply"
    )
    input_column: str = Field(
        ...,
        description="Name of the column containing text to process"
    )
    output_column: Optional[str] = Field(
        None,
        description="Name of the column to store processed text"
    )
    batch_size: Optional[int] = Field(
        1000,
        description="Number of rows to process at once"
    )

class ProcessingResponse(BaseModel):
    file_id: str = Field(..., description="Unique identifier for the file")
    status: str = Field(..., description="Current status of the processing")
    message: str = Field(..., description="Status message")
    result_file: Optional[str] = Field(
        None,
        description="Name of the processed file (if available)"
    )
    progress: Optional[float] = Field(
        None,
        description="Processing progress (0-100)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if processing failed"
    )
