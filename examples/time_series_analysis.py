import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core.parallel import ParallelPipeline
from src.transformers.advanced import TimeFeatureTransformer, OutlierTransformer
from src.validators.advanced import StatisticalValidator, CompletionRateValidator
from src.core.export import DataExporter

def create_time_series_data(size: int = 10000):
    """Create sample time series data with trends, seasonality, and noise"""
    np.random.seed(42)
    
    # Generate dates
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(hours=x) for x in range(size)]
    
    # Create trend
    trend = np.linspace(0, 100, size)
    
    # Create seasonality (daily and weekly patterns)
    daily_pattern = 10 * np.sin(2 * np.pi * np.arange(size) / 24)
    weekly_pattern = 20 * np.sin(2 * np.pi * np.arange(size) / (24 * 7))
    
    # Add noise
    noise = np.random.normal(0, 5, size)
    
    # Combine components
    values = trend + daily_pattern + weekly_pattern + noise
    
    # Create DataFrame
    data = pd.DataFrame({
        'timestamp': dates,
        'value': values,
        'sensor_id': np.random.choice(['A1', 'A2', 'B1', 'B2'], size),
        'temperature': values * 0.1 + np.random.normal(20, 2, size),
        'humidity': np.random.normal(60, 10, size)
    })
    
    # Add some missing values
    data.loc[np.random.choice(size, 100), 'value'] = np.nan
    
    return data

def main():
    # Create sample data
    print("Creating time series data...")
    data = create_time_series_data()
    
    # Create pipeline
    pipeline = ParallelPipeline("time_series_pipeline", n_jobs=4)
    
    # Add validators
    print("\nAdding validators...")
    pipeline.add_validator(CompletionRateValidator({
        'value': 0.99,  # 99% completion rate required
        'temperature': 1.0,
        'humidity': 1.0
    }))
    
    pipeline.add_validator(StatisticalValidator([
        {
            'column': 'temperature',
            'type': 'mean',
            'min_value': 15,
            'max_value': 25
        },
        {
            'column': 'humidity',
            'type': 'mean',
            'min_value': 40,
            'max_value': 80
        }
    ]))
    
    # Add transformers
    print("Adding transformers...")
    
    # Extract time features
    pipeline.add_transformer(TimeFeatureTransformer({
        'timestamp': ['hour', 'dayofweek', 'month', 'quarter']
    }))
    
    # Handle outliers
    pipeline.add_transformer(OutlierTransformer(
        columns=['value', 'temperature', 'humidity'],
        method='iqr',
        threshold=2.0
    ))
    
    # Add rolling statistics transformer
    from src.transformers.time_series import (
        RollingStatisticsTransformer,
        SeasonalDecompositionTransformer,
        LagFeatureTransformer
    )
    
    # Add rolling statistics
    pipeline.add_transformer(RollingStatisticsTransformer(
        columns=['value'],
        windows=[24, 168],  # 24 hours and 1 week
        statistics=['mean', 'std', 'min', 'max']
    ))
    
    # Add seasonal decomposition
    pipeline.add_transformer(SeasonalDecompositionTransformer(
        column='value',
        period=24,  # Daily seasonality
        extrapolate_missing=True
    ))
    
    # Add lag features
    pipeline.add_transformer(LagFeatureTransformer(
        columns=['value'],
        lags=[1, 24, 168],  # Previous hour, day, and week
        group_by='sensor_id'  # Create lags per sensor
    ))
    
    # Process data
    print("\nProcessing data...")
    try:
        processed_data = pipeline.process(data)
        print("\nProcessed data shape:", processed_data.shape)
        print("\nProcessed data columns:", processed_data.columns.tolist())
        
        # Export data
        print("\nExporting data...")
        export_dir = "exported_data/time_series"
        import os
        os.makedirs(export_dir, exist_ok=True)
        
        # Export to different formats
        DataExporter.export(processed_data, 'parquet', 
                          f"{export_dir}/time_series_data.parquet",
                          compression='snappy')
        
        # Export aggregated statistics
        agg_stats = processed_data.groupby('sensor_id').agg({
            'value': ['mean', 'std', 'min', 'max'],
            'temperature': ['mean', 'min', 'max'],
            'humidity': ['mean', 'min', 'max']
        }).round(2)
        
        DataExporter.export(agg_stats, 'csv', 
                          f"{export_dir}/aggregated_stats.csv")
        
        print("\nPipeline metadata:", pipeline.metadata)
        
    except ValueError as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()
