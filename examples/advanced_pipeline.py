import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core.parallel import ParallelPipeline, ParallelFeatureEngineering
from src.transformers.advanced import (
    TextCleanerTransformer,
    OutlierTransformer,
    CategoryEncoderTransformer,
    TimeFeatureTransformer
)
from src.validators.advanced import (
    StatisticalValidator,
    CorrelationValidator,
    CompletionRateValidator,
    PatternValidator
)
from src.core.export import DataExporter

def create_sample_data(size: int = 10000):
    """Create sample data for demonstration"""
    np.random.seed(42)
    
    # Generate dates
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(hours=x) for x in range(size)]
    
    # Generate data
    data = pd.DataFrame({
        'timestamp': dates,
        'value': np.random.normal(100, 15, size),
        'category': np.random.choice(['A', 'B', 'C'], size),
        'text_field': [f"Item_{x} #{'good' if x % 2 == 0 else 'bad'}" for x in range(size)],
        'correlation_field': np.random.normal(100, 15, size) + np.random.normal(0, 2, size)
    })
    
    # Add some outliers
    data.loc[np.random.choice(size, 50), 'value'] = np.random.normal(200, 30, 50)
    
    # Add some missing values
    data.loc[np.random.choice(size, 100), 'category'] = np.nan
    
    return data

def main():
    # Create sample data
    print("Creating sample data...")
    data = create_sample_data()
    
    # Create parallel pipeline
    pipeline = ParallelPipeline("advanced_pipeline", n_jobs=4)
    
    # Add validators
    print("\nAdding validators...")
    pipeline.add_validator(CompletionRateValidator({
        'category': 0.95,  # 95% completion rate required
        'value': 1.0      # 100% completion rate required
    }))
    
    pipeline.add_validator(StatisticalValidator([
        {
            'column': 'value',
            'type': 'mean',
            'min_value': 80,
            'max_value': 120
        }
    ]))
    
    pipeline.add_validator(CorrelationValidator([
        {
            'column1': 'value',
            'column2': 'correlation_field',
            'min_corr': 0.5
        }
    ]))
    
    pipeline.add_validator(PatternValidator({
        'text_field': r'^Item_\d+\s#(good|bad)$'
    }))
    
    # Add transformers
    print("Adding transformers...")
    pipeline.add_transformer(TextCleanerTransformer(
        columns=['text_field'],
        lower=True,
        remove_special_chars=True
    ))
    
    pipeline.add_transformer(OutlierTransformer(
        columns=['value'],
        method='iqr',
        threshold=1.5
    ))
    
    pipeline.add_transformer(CategoryEncoderTransformer({
        'category': 'onehot'
    }))
    
    pipeline.add_transformer(TimeFeatureTransformer({
        'timestamp': ['hour', 'dayofweek', 'month']
    }))
    
    pipeline.add_transformer(ParallelFeatureEngineering([
        {
            'type': 'window',
            'columns': ['value'],
            'operation': 'mean',
            'window': 24,  # 24-hour moving average
            'new_column': 'value_ma24'
        },
        {
            'type': 'arithmetic',
            'columns': ['value', 'correlation_field'],
            'operation': 'sum',
            'new_column': 'value_sum'
        }
    ]))
    
    # Process data
    print("\nProcessing data...")
    try:
        processed_data = pipeline.process(data)
        print("\nProcessed data shape:", processed_data.shape)
        print("\nProcessed data columns:", processed_data.columns.tolist())
        
        # Export data to different formats
        print("\nExporting data...")
        export_dir = "exported_data"
        import os
        os.makedirs(export_dir, exist_ok=True)
        
        DataExporter.export(processed_data, 'csv', f"{export_dir}/data.csv")
        DataExporter.export(processed_data, 'parquet', f"{export_dir}/data.parquet")
        DataExporter.export(
            processed_data, 
            'sqlite', 
            f"{export_dir}/data.db",
            table_name='processed_data'
        )
        
        print("\nPipeline metadata:", pipeline.metadata)
        
    except ValueError as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()
