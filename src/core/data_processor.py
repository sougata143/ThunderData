from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import json
from src.transformers.text import (
    TokenizationTransformer,
    StopwordRemovalTransformer,
    LemmatizationTransformer,
    TextVectorizationTransformer,
    NamedEntityTransformer
)

class DataProcessor:
    """Handles processing of user input data files with configurable text transformations."""
    
    SUPPORTED_FILE_TYPES = {'.csv', '.txt', '.json', '.xlsx'}
    SUPPORTED_TRANSFORMATIONS = {
        'tokenize': TokenizationTransformer,
        'remove_stopwords': StopwordRemovalTransformer,
        'lemmatize': LemmatizationTransformer,
        'vectorize': TextVectorizationTransformer,
        'extract_entities': NamedEntityTransformer
    }
    
    def __init__(self):
        """Initialize the data processor."""
        self.data = None
        self.transformers = []
    
    def load_data(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Load data from various file formats.
        
        Args:
            file_path: Path to the input file
            **kwargs: Additional arguments for reading the file
            
        Returns:
            Loaded DataFrame
        
        Raises:
            ValueError: If file type is not supported
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if path.suffix not in self.SUPPORTED_FILE_TYPES:
            raise ValueError(f"Unsupported file type. Supported types: {self.SUPPORTED_FILE_TYPES}")
        
        if path.suffix == '.csv':
            self.data = pd.read_csv(file_path, **kwargs)
        elif path.suffix == '.json':
            self.data = pd.read_json(file_path, **kwargs)
        elif path.suffix == '.xlsx':
            self.data = pd.read_excel(file_path, **kwargs)
        elif path.suffix == '.txt':
            # For text files, create a single column DataFrame
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.readlines()
            self.data = pd.DataFrame({'text': text})
        
        return self.data
    
    def configure_transformations(self, config: List[Dict[str, Any]]):
        """
        Configure text transformations based on user specifications.
        
        Args:
            config: List of transformation configurations
                Each config should have:
                - 'type': transformation type
                - 'columns': columns to transform
                - Additional parameters specific to the transformer
        
        Raises:
            ValueError: If transformation type is not supported
        """
        self.transformers = []
        
        for transform_config in config:
            transform_type = transform_config.pop('type', None)
            if not transform_type:
                raise ValueError("Transformation type must be specified")
            
            if transform_type not in self.SUPPORTED_TRANSFORMATIONS:
                raise ValueError(f"Unsupported transformation: {transform_type}. "
                              f"Supported types: {list(self.SUPPORTED_TRANSFORMATIONS.keys())}")
            
            transformer_class = self.SUPPORTED_TRANSFORMATIONS[transform_type]
            transformer = transformer_class(**transform_config)
            self.transformers.append(transformer)
    
    def process_data(self) -> pd.DataFrame:
        """
        Apply configured transformations to the data.
        
        Returns:
            Processed DataFrame
        
        Raises:
            ValueError: If no data is loaded or no transformations are configured
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if not self.transformers:
            raise ValueError("No transformations configured. Call configure_transformations() first.")
        
        result = self.data.copy()
        for transformer in self.transformers:
            result = transformer.transform(result)
        
        return result
    
    def save_results(self, output_path: str, format: str = 'csv', **kwargs):
        """
        Save processed data to a file.
        
        Args:
            output_path: Path to save the results
            format: Output format ('csv', 'json', or 'xlsx')
            **kwargs: Additional arguments for saving the file
        
        Raises:
            ValueError: If format is not supported
        """
        if self.data is None:
            raise ValueError("No data to save. Process data first.")
            
        if format not in ['csv', 'json', 'xlsx']:
            raise ValueError("Unsupported output format. Use 'csv', 'json', or 'xlsx'")
        
        save_path = Path(output_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'csv':
            self.data.to_csv(output_path, **kwargs)
        elif format == 'json':
            self.data.to_json(output_path, **kwargs)
        elif format == 'xlsx':
            self.data.to_excel(output_path, **kwargs)
