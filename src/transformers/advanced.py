from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from ..core.pipeline import DataTransformer

class TextCleanerTransformer(DataTransformer):
    """Cleans text data by removing special characters, extra spaces, etc."""
    def __init__(self, columns: List[str], lower: bool = True, remove_special_chars: bool = True):
        self.columns = columns
        self.lower = lower
        self.remove_special_chars = remove_special_chars
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        for column in self.columns:
            if self.lower:
                df[column] = df[column].str.lower()
            if self.remove_special_chars:
                df[column] = df[column].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
            df[column] = df[column].str.strip()
        return df

class OutlierTransformer(DataTransformer):
    """Handles outliers using various methods (IQR, Z-score, or custom ranges)"""
    def __init__(self, columns: List[str], method: str = 'iqr', threshold: float = 1.5):
        self.columns = columns
        self.method = method
        self.threshold = threshold
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        for column in self.columns:
            if self.method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - self.threshold * IQR
                upper_bound = Q3 + self.threshold * IQR
                df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
            elif self.method == 'zscore':
                mean = df[column].mean()
                std = df[column].std()
                df[column] = df[column].clip(
                    lower=mean - self.threshold * std,
                    upper=mean + self.threshold * std
                )
        return df

class FeatureEngineeringTransformer(DataTransformer):
    """Creates new features based on existing columns"""
    def __init__(self, operations: List[Dict[str, Any]]):
        """
        operations format:
        [
            {
                'type': 'arithmetic',  # or 'window', 'interaction'
                'columns': ['col1', 'col2'],
                'operation': '+',  # or 'mean', 'product', etc.
                'new_column': 'new_col_name'
            }
        ]
        """
        self.operations = operations
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
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

class CategoryEncoderTransformer(DataTransformer):
    """Encodes categorical variables using various methods"""
    def __init__(self, columns: Dict[str, str]):
        """
        columns format: {'column_name': 'encoding_type'}
        encoding_type options: 'onehot', 'label', 'target'
        """
        self.columns = columns
        self.encoders = {}
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        for column, encoding in self.columns.items():
            if encoding == 'onehot':
                dummies = pd.get_dummies(df[column], prefix=column)
                df = pd.concat([df, dummies], axis=1)
                df.drop(columns=[column], inplace=True)
            elif encoding == 'label':
                if column not in self.encoders:
                    self.encoders[column] = {
                        val: idx for idx, val in enumerate(df[column].unique())
                    }
                df[column] = df[column].map(self.encoders[column])
        return df

class TimeFeatureTransformer(DataTransformer):
    """Extracts various time-based features from datetime columns"""
    def __init__(self, datetime_columns: Dict[str, List[str]]):
        """
        datetime_columns format: {
            'column_name': ['hour', 'dayofweek', 'month', 'year', 'quarter']
        }
        """
        self.datetime_columns = datetime_columns
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        for column, features in self.datetime_columns.items():
            for feature in features:
                if feature == 'hour':
                    df[f'{column}_hour'] = df[column].dt.hour
                elif feature == 'dayofweek':
                    df[f'{column}_dayofweek'] = df[column].dt.dayofweek
                elif feature == 'month':
                    df[f'{column}_month'] = df[column].dt.month
                elif feature == 'year':
                    df[f'{column}_year'] = df[column].dt.year
                elif feature == 'quarter':
                    df[f'{column}_quarter'] = df[column].dt.quarter
        return df
