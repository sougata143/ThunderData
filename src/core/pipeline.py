from typing import List, Any, Dict, Optional
from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer(ABC):
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

class DataValidator(ABC):
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> bool:
        pass

class Pipeline:
    def __init__(self, name: str):
        self.name = name
        self.transformers: List[DataTransformer] = []
        self.validators: List[DataValidator] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now(),
            "last_run": None,
            "runs": 0
        }
    
    def add_transformer(self, transformer: DataTransformer) -> None:
        """Add a transformer to the pipeline."""
        self.transformers.append(transformer)
        logger.info(f"Added transformer: {transformer.__class__.__name__}")
    
    def add_validator(self, validator: DataValidator) -> None:
        """Add a validator to the pipeline."""
        self.validators.append(validator)
        logger.info(f"Added validator: {validator.__class__.__name__}")
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process data through the pipeline."""
        logger.info(f"Starting pipeline: {self.name}")
        
        # Validate input data
        for validator in self.validators:
            if not validator.validate(data):
                raise ValueError(f"Data validation failed: {validator.__class__.__name__}")
        
        # Transform data
        processed_data = data.copy()
        for transformer in self.transformers:
            processed_data = transformer.transform(processed_data)
            logger.info(f"Applied transformer: {transformer.__class__.__name__}")
        
        # Update metadata
        self.metadata["last_run"] = datetime.now()
        self.metadata["runs"] += 1
        
        logger.info(f"Pipeline {self.name} completed successfully")
        return processed_data
