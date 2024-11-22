from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from ..core.pipeline import DataValidator

class StatisticalValidator(DataValidator):
    """Validates statistical properties of numerical columns"""
    def __init__(self, checks: List[Dict[str, Any]]):
        """
        checks format:
        [
            {
                'column': 'column_name',
                'type': 'mean',  # or 'std', 'median', 'skew'
                'min_value': float,
                'max_value': float
            }
        ]
        """
        self.checks = checks
    
    def validate(self, data: pd.DataFrame) -> bool:
        for check in self.checks:
            column = check['column']
            if check['type'] == 'mean':
                value = data[column].mean()
            elif check['type'] == 'std':
                value = data[column].std()
            elif check['type'] == 'median':
                value = data[column].median()
            elif check['type'] == 'skew':
                value = data[column].skew()
            
            if value < check.get('min_value', float('-inf')) or \
               value > check.get('max_value', float('inf')):
                return False
        return True

class CorrelationValidator(DataValidator):
    """Validates correlation between columns"""
    def __init__(self, column_pairs: List[Dict[str, Any]]):
        """
        column_pairs format:
        [
            {
                'column1': 'col1',
                'column2': 'col2',
                'min_corr': float,
                'max_corr': float
            }
        ]
        """
        self.column_pairs = column_pairs
    
    def validate(self, data: pd.DataFrame) -> bool:
        for pair in self.column_pairs:
            corr = data[pair['column1']].corr(data[pair['column2']])
            if corr < pair.get('min_corr', float('-inf')) or \
               corr > pair.get('max_corr', float('inf')):
                return False
        return True

class CompletionRateValidator(DataValidator):
    """Validates the completion rate of columns"""
    def __init__(self, thresholds: Dict[str, float]):
        """
        thresholds format: {'column_name': minimum_completion_rate}
        """
        self.thresholds = thresholds
    
    def validate(self, data: pd.DataFrame) -> bool:
        for column, threshold in self.thresholds.items():
            completion_rate = 1 - (data[column].isna().sum() / len(data))
            if completion_rate < threshold:
                return False
        return True

class CardinalityValidator(DataValidator):
    """Validates the cardinality (number of unique values) in columns"""
    def __init__(self, limits: Dict[str, Dict[str, int]]):
        """
        limits format: {
            'column_name': {
                'min_unique': int,
                'max_unique': int
            }
        }
        """
        self.limits = limits
    
    def validate(self, data: pd.DataFrame) -> bool:
        for column, limit in self.limits.items():
            unique_count = data[column].nunique()
            if unique_count < limit.get('min_unique', 0) or \
               unique_count > limit.get('max_unique', float('inf')):
                return False
        return True

class PatternValidator(DataValidator):
    """Validates text patterns in columns using regex"""
    def __init__(self, patterns: Dict[str, str]):
        """
        patterns format: {'column_name': 'regex_pattern'}
        """
        self.patterns = patterns
    
    def validate(self, data: pd.DataFrame) -> bool:
        for column, pattern in self.patterns.items():
            if not data[column].str.match(pattern).all():
                return False
        return True
