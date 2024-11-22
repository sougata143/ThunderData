import pandas as pd
import numpy as np
from src.core.parallel import ParallelPipeline
from src.transformers.advanced import TextCleanerTransformer
from src.validators.advanced import PatternValidator, CompletionRateValidator
from src.core.export import DataExporter
from src.transformers.text import (
    TokenizationTransformer,
    StopwordRemovalTransformer,
    LemmatizationTransformer,
    TextVectorizationTransformer,
    NamedEntityTransformer
)

def create_text_data(size: int = 1000):
    """Create sample text data"""
    # Sample product reviews
    products = ['laptop', 'smartphone', 'tablet', 'headphones']
    adjectives = ['great', 'good', 'excellent', 'poor', 'bad', 'amazing']
    features = ['battery life', 'screen', 'performance', 'design', 'price']
    
    def generate_review():
        product = np.random.choice(products)
        adj = np.random.choice(adjectives)
        feature = np.random.choice(features)
        rating = np.random.randint(1, 6)
        
        templates = [
            f"The {product} has {adj} {feature}. I rate it {rating}/5.",
            f"I bought this {product} last week. The {feature} is {adj}.",
            f"This {product}'s {feature} is {adj}. Recommended!" if rating > 3 else f"This {product}'s {feature} is {adj}. Not recommended.",
            f"Just got the new {product}. {feature.capitalize()} is {adj}!",
        ]
        
        review = np.random.choice(templates)
        return review, product, rating
    
    # Generate data
    reviews, products_list, ratings = zip(*[generate_review() for _ in range(size)])
    
    # Create DataFrame
    data = pd.DataFrame({
        'review_text': reviews,
        'product': products_list,
        'rating': ratings,
        'timestamp': pd.date_range(start='2023-01-01', periods=size, freq='H')
    })
    
    # Add some missing values and special characters
    data.loc[np.random.choice(size, 50), 'review_text'] = np.nan
    data['review_text'] = data['review_text'].fillna('')
    
    # Add some noise and special characters
    noise_chars = ['!!!', '...', '#', '@', '$']
    for idx in np.random.choice(size, 200):
        noise = ' '.join(np.random.choice(noise_chars, 2))
        data.loc[idx, 'review_text'] += f" {noise}"
    
    return data

def main():
    # Create sample data
    print("Creating text data...")
    data = create_text_data()
    
    # Create pipeline
    pipeline = ParallelPipeline("text_processing_pipeline", n_jobs=4)
    
    # Add validators
    print("\nAdding validators...")
    pipeline.add_validator(CompletionRateValidator({
        'review_text': 0.95,  # 95% completion rate required
        'product': 1.0,
        'rating': 1.0
    }))
    
    # Add transformers
    print("Adding transformers...")
    
    # Clean text
    pipeline.add_transformer(TextCleanerTransformer(
        columns=['review_text'],
        lower=True,
        remove_special_chars=True
    ))
    
    # Tokenize text
    pipeline.add_transformer(TokenizationTransformer(
        columns=['review_text']
    ))
    
    # Remove stopwords
    pipeline.add_transformer(StopwordRemovalTransformer(
        columns=['review_text']
    ))
    
    # Lemmatize text
    pipeline.add_transformer(LemmatizationTransformer(
        columns=['review_text']
    ))
    
    # Extract named entities
    pipeline.add_transformer(NamedEntityTransformer(
        columns=['review_text'],
        entity_types=['PRODUCT', 'ORG']
    ))
    
    # Vectorize text
    pipeline.add_transformer(TextVectorizationTransformer(
        columns=['review_text'],
        method='tfidf',
        max_features=100
    ))
    
    # Process data
    print("\nProcessing data...")
    try:
        processed_data = pipeline.process(data)
        print("\nProcessed data shape:", processed_data.shape)
        print("\nProcessed data columns:", processed_data.columns.tolist())
        
        # Export data
        print("\nExporting data...")
        export_dir = "exported_data/text_processing"
        import os
        os.makedirs(export_dir, exist_ok=True)
        
        # Export processed data
        DataExporter.export(processed_data, 'parquet', 
                          f"{export_dir}/processed_text.parquet",
                          compression='snappy')
        
        # Export summary statistics
        summary_stats = pd.DataFrame({
            'avg_rating_by_product': processed_data.groupby('product')['rating'].mean(),
            'review_count_by_product': processed_data.groupby('product').size(),
            'avg_text_length': processed_data['review_text'].str.len().mean(),
            'unique_entities': processed_data['review_text_entities'].nunique()
        }).round(2)
        
        DataExporter.export(summary_stats, 'csv',
                          f"{export_dir}/text_summary_stats.csv")
        
        print("\nPipeline metadata:", pipeline.metadata)
        
    except ValueError as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()
