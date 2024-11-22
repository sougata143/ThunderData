from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from ..core.pipeline import DataTransformer

class RollingStatisticsTransformer(DataTransformer):
    """Calculates rolling statistics for time series data"""
    
    def __init__(self, columns: List[str], windows: List[int], 
                 statistics: List[str] = ['mean', 'std']):
        """
        Args:
            columns: List of columns to calculate rolling statistics for
            windows: List of window sizes
            statistics: List of statistics to calculate ('mean', 'std', 'min', 'max')
        """
        self.columns = columns
        self.windows = windows
        self.statistics = statistics
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        for col in self.columns:
            for window in self.windows:
                rolling = df[col].rolling(window=window, min_periods=1)
                
                for stat in self.statistics:
                    if stat == 'mean':
                        df[f'{col}_rolling_mean_{window}'] = rolling.mean()
                    elif stat == 'std':
                        df[f'{col}_rolling_std_{window}'] = rolling.std()
                    elif stat == 'min':
                        df[f'{col}_rolling_min_{window}'] = rolling.min()
                    elif stat == 'max':
                        df[f'{col}_rolling_max_{window}'] = rolling.max()
        
        return df

class SeasonalDecompositionTransformer(DataTransformer):
    """Performs seasonal decomposition of time series data"""
    
    def __init__(self, column: str, period: int, model: str = 'additive',
                 extrapolate_missing: bool = True):
        """
        Args:
            column: Column to decompose
            period: Number of periods in seasonality
            model: Type of seasonal component ('additive' or 'multiplicative')
            extrapolate_missing: Whether to extrapolate missing values
        """
        self.column = column
        self.period = period
        self.model = model
        self.extrapolate_missing = extrapolate_missing
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Handle missing values if needed
        if self.extrapolate_missing:
            df[self.column] = df[self.column].interpolate(method='linear')
        
        # Perform decomposition
        decomposition = seasonal_decompose(
            df[self.column],
            period=self.period,
            model=self.model
        )
        
        # Add components as new columns
        df[f'{self.column}_trend'] = decomposition.trend
        df[f'{self.column}_seasonal'] = decomposition.seasonal
        df[f'{self.column}_residual'] = decomposition.resid
        
        # Fill any remaining NaN values
        for col in df.columns:
            if col.startswith(f'{self.column}_'):
                df[col] = df[col].fillna(method='bfill').fillna(method='ffill')
        
        return df

class LagFeatureTransformer(DataTransformer):
    """Creates lag features for time series data"""
    
    def __init__(self, columns: List[str], lags: List[int], 
                 group_by: Optional[str] = None):
        """
        Args:
            columns: Columns to create lag features for
            lags: List of lag periods
            group_by: Optional column to group by before creating lags
        """
        self.columns = columns
        self.lags = lags
        self.group_by = group_by
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        if self.group_by:
            for col in self.columns:
                for lag in self.lags:
                    df[f'{col}_lag_{lag}'] = df.groupby(self.group_by)[col].shift(lag)
        else:
            for col in self.columns:
                for lag in self.lags:
                    df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        # Fill NaN values created by lagging
        for col in df.columns:
            if '_lag_' in col:
                df[col] = df[col].fillna(method='bfill').fillna(method='ffill')
        
        return df

class DifferenceTransformer(DataTransformer):
    """Creates difference features for time series data"""
    
    def __init__(self, columns: List[str], periods: List[int] = [1],
                 orders: List[int] = [1], group_by: Optional[str] = None):
        """
        Args:
            columns: Columns to create differences for
            periods: Periods to difference over
            orders: Orders of differencing
            group_by: Optional column to group by before differencing
        """
        self.columns = columns
        self.periods = periods
        self.orders = orders
        self.group_by = group_by
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        for col in self.columns:
            for period in self.periods:
                for order in self.orders:
                    if self.group_by:
                        diff = df.groupby(self.group_by)[col].diff(period)
                        for _ in range(order - 1):
                            diff = diff.groupby(self.group_by).diff(period)
                    else:
                        diff = df[col].diff(period)
                        for _ in range(order - 1):
                            diff = diff.diff(period)
                    
                    df[f'{col}_diff_p{period}_o{order}'] = diff
        
        # Fill NaN values created by differencing
        for col in df.columns:
            if '_diff_' in col:
                df[col] = df[col].fillna(method='bfill').fillna(method='ffill')
        
        return df
