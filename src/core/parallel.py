from typing import List, Callable, Any, Dict, Optional
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
import multiprocessing
from ..core.pipeline import Pipeline, DataTransformer

class ParallelPipeline(Pipeline):
    """Pipeline with parallel processing capabilities"""
    
    def __init__(self, name: str, n_jobs: int = -1, backend: str = 'process'):
        super().__init__(name)
        self.n_jobs = n_jobs if n_jobs > 0 else multiprocessing.cpu_count()
        self.backend = backend
    
    def _process_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Process a single chunk of data through the pipeline"""
        # Apply validators
        for validator in self.validators:
            if not validator.validate(chunk):
                raise ValueError(f"Data validation failed: {validator.__class__.__name__}")
        
        # Apply transformers
        processed_chunk = chunk.copy()
        for transformer in self.transformers:
            processed_chunk = transformer.transform(processed_chunk)
        
        return processed_chunk
    
    def process(self, data: pd.DataFrame, chunk_size: Optional[int] = None) -> pd.DataFrame:
        """
        Process data in parallel using multiple cores
        
        Args:
            data: Input DataFrame
            chunk_size: Size of each data chunk for parallel processing
        """
        if chunk_size is None:
            chunk_size = len(data) // (self.n_jobs * 4)
            chunk_size = max(chunk_size, 1000)  # Minimum chunk size
        
        chunks = [data.iloc[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        # Choose executor based on backend
        Executor = ProcessPoolExecutor if self.backend == 'process' else ThreadPoolExecutor
        
        with Executor(max_workers=self.n_jobs) as executor:
            processed_chunks = list(executor.map(self._process_chunk, chunks))
        
        # Combine processed chunks
        result = pd.concat(processed_chunks, axis=0)
        
        # Update metadata
        self.metadata["last_run"] = pd.Timestamp.now()
        self.metadata["runs"] += 1
        self.metadata["chunks_processed"] = len(chunks)
        
        return result

class ParallelTransformer(DataTransformer):
    """Base class for transformers that support parallel processing"""
    
    def __init__(self, n_jobs: int = -1, backend: str = 'process'):
        self.n_jobs = n_jobs if n_jobs > 0 else multiprocessing.cpu_count()
        self.backend = backend
    
    def _transform_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Transform a single chunk of data"""
        raise NotImplementedError("Subclasses must implement _transform_chunk")
    
    def transform(self, data: pd.DataFrame, chunk_size: Optional[int] = None) -> pd.DataFrame:
        """Transform data in parallel"""
        if chunk_size is None:
            chunk_size = len(data) // (self.n_jobs * 4)
            chunk_size = max(chunk_size, 1000)
        
        chunks = [data.iloc[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        Executor = ProcessPoolExecutor if self.backend == 'process' else ThreadPoolExecutor
        
        with Executor(max_workers=self.n_jobs) as executor:
            transformed_chunks = list(executor.map(self._transform_chunk, chunks))
        
        return pd.concat(transformed_chunks, axis=0)

class ParallelFeatureEngineering(ParallelTransformer):
    """Parallel implementation of feature engineering"""
    
    def __init__(self, operations: List[Dict[str, Any]], **kwargs):
        super().__init__(**kwargs)
        self.operations = operations
    
    def _transform_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        df = chunk.copy()
        for op in self.operations:
            if op['type'] == 'arithmetic':
                df[op['new_column']] = df[op['columns']].agg(op['operation'], axis=1)
            elif op['type'] == 'window':
                df[op['new_column']] = df[op['columns'][0]].rolling(
                    window=op.get('window', 3)
                ).agg(op['operation'])
            elif op['type'] == 'interaction':
                df[op['new_column']] = df[op['columns'][0]] * df[op['columns'][1]]
        return df
