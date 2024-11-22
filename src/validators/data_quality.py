from typing import List, Dict, Any, Optional
import pandas as pd
from ..core.pipeline import DataValidator

class ColumnExistenceValidator(DataValidator):
    def __init__(self, required_columns: List[str]):
        self.required_columns = required_columns
    
    def validate(self, data: pd.DataFrame) -> bool:
        return all(col in data.columns for col in self.required_columns)

class DataTypeValidator(DataValidator):
    def __init__(self, dtype_requirements: Dict[str, str]):
        self.dtype_requirements = dtype_requirements
    
    def validate(self, data: pd.DataFrame) -> bool:
        for column, expected_dtype in self.dtype_requirements.items():
            if column not in data.columns:
                return False
            if str(data[column].dtype) != expected_dtype:
                return False
        return True

class ValueRangeValidator(DataValidator):
    def __init__(self, ranges: Dict[str, Dict[str, float]]):
        """
        ranges format: {
            'column_name': {
                'min': min_value,
                'max': max_value
            }
        }
        """
        self.ranges = ranges
    
    def validate(self, data: pd.DataFrame) -> bool:
        for column, range_values in self.ranges.items():
            if column not in data.columns:
                return False
            
            min_val = range_values.get('min')
            max_val = range_values.get('max')
            
            if min_val is not None and data[column].min() < min_val:
                return False
            if max_val is not None and data[column].max() > max_val:
                return False
        
        return True

class UniqueValidator(DataValidator):
    def __init__(self, columns: List[str]):
        self.columns = columns
    
    def validate(self, data: pd.DataFrame) -> bool:
        for column in self.columns:
            if column not in data.columns:
                return False
            if data[column].duplicated().any():
                return False
        return True
