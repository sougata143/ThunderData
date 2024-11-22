from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from ..core.pipeline import DataTransformer

class DropNATransformer(DataTransformer):
    def __init__(self, columns: Optional[List[str]] = None):
        self.columns = columns
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.dropna(subset=self.columns) if self.columns else data.dropna()

class TypeConversionTransformer(DataTransformer):
    def __init__(self, type_mapping: Dict[str, str]):
        self.type_mapping = type_mapping
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        for column, dtype in self.type_mapping.items():
            df[column] = df[column].astype(dtype)
        return df

class StandardScalerTransformer(DataTransformer):
    def __init__(self, columns: List[str]):
        self.columns = columns
        self.mean: Dict[str, float] = {}
        self.std: Dict[str, float] = {}
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        for column in self.columns:
            self.mean[column] = df[column].mean()
            self.std[column] = df[column].std()
            df[column] = (df[column] - self.mean[column]) / self.std[column]
        return df

class DatetimeTransformer(DataTransformer):
    def __init__(self, columns: List[str], format: Optional[str] = None):
        self.columns = columns
        self.format = format
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        for column in self.columns:
            df[column] = pd.to_datetime(df[column], format=self.format)
        return df
