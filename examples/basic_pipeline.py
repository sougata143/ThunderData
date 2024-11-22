import pandas as pd
import numpy as np
from src.core.pipeline import Pipeline
from src.transformers.common import (
    DropNATransformer,
    TypeConversionTransformer,
    StandardScalerTransformer,
    DatetimeTransformer
)
from src.validators.data_quality import (
    ColumnExistenceValidator,
    DataTypeValidator,
    ValueRangeValidator
)

def main():
    # Create sample data
    data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
        'value': ['100', '150', '200', '250'],
        'category': ['A', 'B', 'A', 'C'],
        'score': [0.5, 0.7, np.nan, 0.9]
    })
    
    # Create a pipeline
    pipeline = Pipeline("sample_pipeline")
    
    # Add validators
    pipeline.add_validator(ColumnExistenceValidator(
        required_columns=['date', 'value', 'category', 'score']
    ))
    pipeline.add_validator(DataTypeValidator({
        'category': 'object'
    }))
    pipeline.add_validator(ValueRangeValidator({
        'score': {'min': 0.0, 'max': 1.0}
    }))
    
    # Add transformers
    pipeline.add_transformer(DropNATransformer(columns=['score']))
    pipeline.add_transformer(TypeConversionTransformer({
        'value': 'float64'
    }))
    pipeline.add_transformer(DatetimeTransformer(
        columns=['date']
    ))
    pipeline.add_transformer(StandardScalerTransformer(
        columns=['value']
    ))
    
    # Process the data
    try:
        processed_data = pipeline.process(data)
        print("\nProcessed Data:")
        print(processed_data)
        print("\nPipeline Metadata:")
        print(pipeline.metadata)
    except ValueError as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()
